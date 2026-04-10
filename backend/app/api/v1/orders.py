import logging
from datetime import datetime, timedelta, timezone

from anthropic import APIStatusError
from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy import inspect as sa_inspect, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.dependencies import get_current_user, get_current_user_optional
from app.models.enums import OrderKind, OrderStatus
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
from app.services.llm.generation_pipeline import (
    run_seo_pipeline_async,
    run_uniquify_pipeline_async,
)

logger = logging.getLogger(__name__)

# Если статус generating «завис» (краш процесса / обрыв), разрешаем новый запуск.
_GENERATION_STUCK_AFTER = timedelta(minutes=15)

router = APIRouter()


def _generation_start_allowed(order: Order) -> tuple[bool, str | None]:
    """
    True — можно ставить generating и звать LLM.
    str — текст 409, если нельзя.
    """
    if order.status == OrderStatus.paid:
        return True, None
    if order.status == OrderStatus.failed:
        return True, None
    if order.status == OrderStatus.generating:
        updated = order.updated_at
        if updated is None:
            return True, None
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) - updated > _GENERATION_STUCK_AFTER:
            logger.warning(
                "generate_order_text: заказ id=%s в generating дольше %s — считаем зависшим, разрешаем повтор",
                order.id,
                _GENERATION_STUCK_AFTER,
            )
            return True, None
        return (
            False,
            "Генерация уже выполняется. Подождите или повторите через несколько минут.",
        )
    return False, "Генерация доступна только для оплаченных заказов."


async def _to_client_order_response(
    session: AsyncSession,
    order: Order,
    *,
    include_source_text: bool = True,
) -> OrderResponse:
    """
    Сериализация заказа в ответ API.

    После UPDATE с server_onupdate (updated_at) атрибуты ORM могут быть «просрочены»;
    синхронный model_validate тогда дергает ленивую загрузку → MissingGreenlet в async.
    """
    if sa_inspect(order).expired_attributes:
        await session.refresh(order)
    payload = OrderResponse.model_validate(order).model_dump()
    if not include_source_text:
        payload["source_text"] = None
    show_text = order.status in (
        OrderStatus.completed,
        OrderStatus.review_required,
        OrderStatus.failed,
    )
    if not show_text:
        payload["generated_text"] = None
    return OrderResponse(**payload)


@router.post("/preview-price", response_model=OrderQuoteResponse)
async def preview_price(
    body: OrderQuotePreview,
    user: User | None = Depends(get_current_user_optional),
) -> OrderQuoteResponse:
    """Пересчёт цены по счётчику слов и пресету; со входом — учёт скидки 30% на первый заказ."""
    try:
        get_voice(body.brand_voice_id)
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    src = (
        (body.source_text or "").strip()
        if body.order_kind == OrderKind.uniquify
        else None
    )
    if user is not None:
        bd = calculate_order_price(
            user,
            body.target_word_count,
            order_kind=body.order_kind,
            source_text=src,
        )
        return OrderQuoteResponse(
            order_kind=body.order_kind,
            target_word_count=body.target_word_count,
            billing_word_count=bd.billing_word_count,
            price_base_cents=bd.price_base_cents,
            discount_cents=bd.discount_cents,
            price_cents=bd.price_cents,
            first_order_bonus_applied=bd.bonus_applied,
        )
    price, bw = quote_price_cents(
        body.target_word_count,
        order_kind=body.order_kind,
        source_text=src,
    )
    return OrderQuoteResponse(
        order_kind=body.order_kind,
        target_word_count=body.target_word_count,
        billing_word_count=bw,
        price_base_cents=price,
        discount_cents=0,
        price_cents=price,
        first_order_bonus_applied=False,
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
    src = (
        (body.source_text or "").strip()
        if body.order_kind == OrderKind.uniquify
        else None
    )
    breakdown = calculate_order_price(
        user,
        body.target_word_count,
        order_kind=body.order_kind,
        source_text=src,
    )
    order = Order(
        user_id=user.id,
        status=OrderStatus.pending_payment,
        order_kind=body.order_kind,
        brand_name=body.brand_name.strip(),
        task_notes=body.task_notes,
        source_text=src,
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
    return await _to_client_order_response(session, order)


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
        order=await _to_client_order_response(session, order),
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

    ok, deny_msg = _generation_start_allowed(order)
    if not ok:
        raise HTTPException(status_code=409, detail=deny_msg or "Нельзя запустить генерацию")

    order.status = OrderStatus.generating
    await session.flush()

    try:
        seo_cfg = SeoOrderConfigSchema.model_validate(order.seo_config)
    except ValidationError as e:
        order.status = OrderStatus.failed
        await session.flush()
        logger.warning(
            "generate_order_text: seo_config order_id=%s validation_errors=%s",
            order_id,
            e.errors(),
        )
        raise HTTPException(
            status_code=422,
            detail="Некорректные SEO-поля в заказе (seo_config). Создай заказ заново или обратись в поддержку.",
        ) from e

    ctx = GenerationContext(
        brand_name=order.brand_name,
        keywords=[str(k) for k in order.keywords],
        lsi_keywords=[str(k) for k in order.lsi_keywords],
        task_notes=order.task_notes,
        target_word_count=order.target_word_count,
        brand_voice_id=order.brand_voice_id,
        seo=seo_cfg,
        order_id=order.id,
    )

    try:
        if order.order_kind == OrderKind.uniquify:
            if not order.source_text or not str(order.source_text).strip():
                order.status = OrderStatus.failed
                await session.flush()
                raise HTTPException(
                    status_code=422,
                    detail="В заказе уникализации отсутствует исходный текст.",
                )
            generated = await run_uniquify_pipeline_async(ctx, order.source_text)
        else:
            generated = await run_seo_pipeline_async(ctx)
    except RuntimeError as e:
        order.status = OrderStatus.failed
        await session.flush()
        raise HTTPException(
            status_code=503,
            detail=str(e),
        ) from e
    except APIStatusError as e:
        order.status = OrderStatus.failed
        await session.flush()
        raise HTTPException(
            status_code=502,
            detail=e.message[:1200],
        ) from e
    except Exception as e:
        order.status = OrderStatus.failed
        await session.flush()
        logger.exception("generate_order_text: непредвиденная ошибка order_id=%s", order_id)
        raise HTTPException(
            status_code=500,
            detail="Ошибка генерации",
        ) from e

    order.generated_text = generated.final_text
    order.status = OrderStatus.review_required
    await session.flush()
    return OrderGenerateResponse(
        order=await _to_client_order_response(session, order),
    )


@router.get("", response_model=list[OrderResponse])
async def list_orders(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> list[OrderResponse]:
    result = await session.execute(
        select(Order).where(Order.user_id == user.id).order_by(Order.created_at.desc())
    )
    rows = list(result.scalars().all())
    return [
        await _to_client_order_response(session, o, include_source_text=False)
        for o in rows
    ]


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
    return await _to_client_order_response(session, order)
