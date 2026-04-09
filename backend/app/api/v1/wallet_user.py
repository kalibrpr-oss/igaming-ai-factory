"""
Пополнение кошелька для авторизованного пользователя.

Тестовый mock-топап включается только флагом окружения (локальная разработка).
Реальная касса (ЮKassa) — отдельный этап.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import get_session
from app.dependencies import get_current_user
from app.models.enums import PaymentKind, PaymentProvider, PaymentStatus
from app.models.payment import Payment
from app.models.user import User
from app.schemas.wallet import UserMockTopupBody, UserMockTopupResponse
from app.services.payments.settlement import SettlementError, apply_payment_succeeded

router = APIRouter()


@router.post(
    "/mock-topup",
    response_model=UserMockTopupResponse,
    summary="Тестовое пополнение баланса (mock)",
)
async def user_mock_topup(
    body: UserMockTopupBody,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> UserMockTopupResponse:
    """
    Создаёт платёж wallet_topup (mock) и сразу зачисляет через apply_payment_succeeded.
    Доступно только если enable_user_wallet_mock_topup=true (никогда на проде).
    """
    if not settings.enable_user_wallet_mock_topup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found",
        )

    payment = Payment(
        user_id=user.id,
        order_id=None,
        kind=PaymentKind.wallet_topup,
        provider=PaymentProvider.mock,
        external_id=f"user-mock-{uuid.uuid4()}",
        amount_cents=body.amount_cents,
        status=PaymentStatus.pending,
    )
    session.add(payment)
    await session.flush()

    try:
        await apply_payment_succeeded(
            session,
            payment.id,
            raw_payload={"source": "user_wallet_mock"},
        )
    except SettlementError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e

    bal = await session.scalar(
        select(User.balance_cents).where(User.id == user.id)
    )
    return UserMockTopupResponse(
        payment_id=payment.id,
        user_balance_cents=int(bal or 0),
    )
