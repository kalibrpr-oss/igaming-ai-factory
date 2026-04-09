from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.dependencies import get_current_admin
from app.models.enums import OrderStatus
from app.models.order import Order
from app.models.user import User
from app.schemas.admin import (
    AdminReviewActionResponse,
    AdminReviewNotesBody,
    AdminReviewOrderRow,
)

router = APIRouter()


@router.get("/review-queue", response_model=list[AdminReviewOrderRow])
async def list_review_queue(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
) -> list[AdminReviewOrderRow]:
    result = await session.execute(
        select(Order)
        .where(Order.status == OrderStatus.review_required)
        .order_by(Order.updated_at.asc())
    )
    orders = list(result.scalars().all())
    return [AdminReviewOrderRow.model_validate(o) for o in orders]


@router.post(
    "/{order_id}/review/approve",
    response_model=AdminReviewActionResponse,
)
async def approve_order_review(
    order_id: int,
    body: AdminReviewNotesBody,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_current_admin),
) -> AdminReviewActionResponse:
    """Одобрить текст после review_required; финальный статус completed."""
    stmt = select(Order).where(Order.id == order_id).with_for_update()
    result = await session.execute(stmt)
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    if order.status != OrderStatus.review_required:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Одобрение доступно только для заказов в статусе review_required",
        )

    now = datetime.now(timezone.utc)
    order.status = OrderStatus.completed
    order.moderated_at = now
    order.moderated_by_user_id = admin.id
    order.moderation_notes = body.notes
    await session.flush()
    await session.refresh(order)

    return AdminReviewActionResponse(
        order_id=order.id,
        status=order.status,
        moderated_at=order.moderated_at,
        moderation_notes=order.moderation_notes,
    )


@router.post(
    "/{order_id}/review/reject",
    response_model=AdminReviewActionResponse,
)
async def reject_order_review(
    order_id: int,
    body: AdminReviewNotesBody,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_current_admin),
) -> AdminReviewActionResponse:
    """
    Отклонить по качеству: возврат в paid без дублирования статуса failed.
    Клиент снова может вызвать POST /orders/{id}/generate.
    """
    stmt = select(Order).where(Order.id == order_id).with_for_update()
    result = await session.execute(stmt)
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    if order.status != OrderStatus.review_required:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Отклонение доступно только для заказов в статусе review_required",
        )

    now = datetime.now(timezone.utc)
    order.status = OrderStatus.paid
    order.moderated_at = now
    order.moderated_by_user_id = admin.id
    order.moderation_notes = body.notes
    await session.flush()
    await session.refresh(order)

    return AdminReviewActionResponse(
        order_id=order.id,
        status=order.status,
        moderated_at=order.moderated_at,
        moderation_notes=order.moderation_notes,
    )
