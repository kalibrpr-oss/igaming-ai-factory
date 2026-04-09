from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.dependencies import get_current_admin
from app.models.enums import PaymentStatus
from app.models.order import Order
from app.models.payment import Payment
from app.models.user import User
from app.schemas.admin import AdminUserRow

router = APIRouter()


@router.get("", response_model=list[AdminUserRow])
async def list_users_with_stats(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
) -> list[AdminUserRow]:
    users_result = await session.execute(
        select(User).order_by(User.created_at.desc())
    )
    users = list(users_result.scalars().all())
    if not users:
        return []

    ids = [u.id for u in users]
    order_counts = await session.execute(
        select(Order.user_id, func.count(Order.id))
        .where(Order.user_id.in_(ids))
        .group_by(Order.user_id)
    )
    oc_map = {row[0]: row[1] for row in order_counts.all()}

    pay_counts = await session.execute(
        select(Payment.user_id, func.count(Payment.id))
        .where(
            Payment.user_id.in_(ids),
            Payment.status == PaymentStatus.succeeded,
        )
        .group_by(Payment.user_id)
    )
    pc_map = {row[0]: row[1] for row in pay_counts.all()}

    return [
        AdminUserRow(
            id=u.id,
            email=u.email,
            username=u.username,
            created_at=u.created_at,
            is_active=u.is_active,
            is_admin=u.is_admin,
            orders_total=oc_map.get(u.id, 0),
            payments_succeeded=pc_map.get(u.id, 0),
        )
        for u in users
    ]
