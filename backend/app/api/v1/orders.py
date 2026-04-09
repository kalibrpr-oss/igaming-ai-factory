from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.dependencies import get_current_user
from app.models.enums import OrderStatus
from app.models.order import Order
from app.models.user import User
from app.prompts.registry import get_voice
from app.schemas.order import (
    OrderCreateRequest,
    OrderGenerateResponse,
    OrderPayResponse,
    OrderQuotePreview,
    OrderQuoteResponse,
    OrderResponse,
)
from app.schemas.seo import SeoOrderConfigSchema
from app.services.orders import OrderPaymentError, apply_order_payment
from app.services.pricing import calculate_order_price, quote_price_cents
from app.prompts.types import GenerationContext
from app.services.llm.generation_pipeline import run_seo_pipeline_async

router = APIRouter()


def _to_client_order_response(order: Order) -> OrderResponse:
    payload = OrderResponse.model_validate(order).model_dump()
    if order.status != OrderStatus.completed:
        payload["generated_text"] = None
    return OrderResponse(**payload)


@router.post("/preview-price", response_model=OrderQuoteResponse)
async def preview_price(body: OrderQuotePreview) -> OrderQuoteResponse:
    """Пересчёт цены по счётчику слов и пресету (без полного ТЗ)."""
    try:
        get_voice(body.brand_voice_id)
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    price = quote_price_cents(body.target_word_count)
    return OrderQuoteResponse(
        target_word_count=body.target_word_count,
        price_base_cents=price,
        discount_cents=0,
        price_cents=price,
    )


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(
    body: OrderCreateRequest,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> OrderResponse:
    try:
        get_voice(body.brand_voice_id)
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    breakdown = calculate_order_price(user, body.target_word_count)
    order = Order(
        user_id=user.id,
        status=OrderStatus.pending_payment,
        brand_name=body.brand_name.strip(),
        task_notes=body.task_notes,
        keywords=body.keywords,
        lsi_keywords=body.lsi_keywords,
        seo_config=body.seo.model_dump(),
        target_word_count=body.target_word_count,
        price_base_cents=breakdown.price_base_cents,
        discount_cents=breakdown.discount_cents,
        price_cents=breakdown.price_cents,
        brand_voice_id=body.brand_voice_id,
    )
    session.add(order)
    await session.flush()
    await session.refresh(order)
    return _to_client_order_response(order)


@router.post("/{order_id}/pay", response_model=OrderPayResponse)
async def pay_order_from_balance(
    order_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> OrderPayResponse:
    own_order = await session.execute(
        select(Order.id).where(Order.id == order_id, Order.user_id == user.id)
    )
    if own_order.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    try:
        order = await apply_order_payment(session, order_id)
    except OrderPaymentError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e

    await session.refresh(user)
    return OrderPayResponse(
        order=_to_client_order_response(order),
        user_balance_cents=user.balance_cents,
    )


@router.post("/{order_id}/generate", response_model=OrderGenerateResponse)
async def generate_order_text(
    order_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> OrderGenerateResponse:
    result = await session.execute(
        select(Order).where(Order.id == order_id, Order.user_id == user.id)
    )
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    if order.status != OrderStatus.paid:
        raise HTTPException(
            status_code=409,
            detail="Генерация доступна только для оплаченных заказов",
        )

    order.status = OrderStatus.generating
    await session.flush()

    ctx = GenerationContext(
        brand_name=order.brand_name,
        keywords=[str(k) for k in order.keywords],
        lsi_keywords=[str(k) for k in order.lsi_keywords],
        task_notes=order.task_notes,
        target_word_count=order.target_word_count,
        brand_voice_id=order.brand_voice_id,
        seo=SeoOrderConfigSchema.model_validate(order.seo_config),
        order_id=order.id,
    )

    try:
        generated = await run_seo_pipeline_async(ctx)
    except Exception as e:
        order.status = OrderStatus.failed
        await session.flush()
        raise HTTPException(status_code=500, detail="Ошибка генерации") from e

    order.generated_text = generated.final_text
    order.status = OrderStatus.review_required
    await session.flush()
    await session.refresh(order)
    return OrderGenerateResponse(order=_to_client_order_response(order))


@router.get("", response_model=list[OrderResponse])
async def list_orders(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> list[OrderResponse]:
    result = await session.execute(
        select(Order).where(Order.user_id == user.id).order_by(Order.created_at.desc())
    )
    return [_to_client_order_response(order) for order in result.scalars().all()]


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> OrderResponse:
    result = await session.execute(
        select(Order).where(Order.id == order_id, Order.user_id == user.id)
    )
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return _to_client_order_response(order)
