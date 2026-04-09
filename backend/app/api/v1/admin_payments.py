from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.dependencies import get_current_admin
from app.models.payment import Payment
from app.models.user import User
from app.schemas.admin import AdminPaymentRow

router = APIRouter()

_PAYMENTS_LIMIT = 200


@router.get("", response_model=list[AdminPaymentRow])
async def list_payments(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
) -> list[AdminPaymentRow]:
    stmt = (
        select(Payment, User.email, User.username)
        .join(User, Payment.user_id == User.id)
        .order_by(Payment.created_at.desc())
        .limit(_PAYMENTS_LIMIT)
    )
    result = await session.execute(stmt)
    rows: list[AdminPaymentRow] = []
    for p, email, username in result.all():
        rows.append(
            AdminPaymentRow(
                id=p.id,
                user_id=p.user_id,
                user_email=email,
                user_username=username,
                order_id=p.order_id,
                kind=p.kind,
                provider=p.provider,
                amount_cents=p.amount_cents,
                currency=p.currency,
                status=p.status,
                created_at=p.created_at,
            )
        )
    return rows
