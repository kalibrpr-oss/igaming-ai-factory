"""
Внутренний тест пополнения кошелька без кассы.
Роутер подключается только при enable_internal_wallet_test_flow=true.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.dependencies import get_current_admin
from app.models.enums import PaymentKind, PaymentProvider, PaymentStatus
from app.models.payment import Payment
from app.models.user import User
from app.schemas.internal_wallet_test import (
    InternalTestTopupConfirmBody,
    InternalTestTopupConfirmed,
    InternalTestTopupCreate,
    InternalTestTopupCreated,
)
from app.services.payments.settlement import SettlementError, apply_payment_succeeded

router = APIRouter()


@router.post(
    "/topups",
    response_model=InternalTestTopupCreated,
    status_code=status.HTTP_201_CREATED,
)
async def create_internal_test_topup(
    body: InternalTestTopupCreate,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
) -> InternalTestTopupCreated:
    """Шаг A: создать pending Payment (wallet_topup, provider=mock)."""
    ur = await session.execute(select(User).where(User.id == body.user_id))
    if ur.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    payment = Payment(
        user_id=body.user_id,
        order_id=None,
        kind=PaymentKind.wallet_topup,
        provider=PaymentProvider.mock,
        external_id=f"mock-{uuid.uuid4()}",
        amount_cents=body.amount_cents,
        status=PaymentStatus.pending,
    )
    session.add(payment)
    await session.flush()

    return InternalTestTopupCreated(
        payment_id=payment.id,
        user_id=payment.user_id,
        amount_cents=payment.amount_cents,
        provider=payment.provider.value,
        kind=payment.kind.value,
        status=payment.status.value,
        external_id=payment.external_id or "",
    )


@router.post("/topups/{payment_id}/confirm", response_model=InternalTestTopupConfirmed)
async def confirm_internal_test_topup(
    payment_id: int,
    body: InternalTestTopupConfirmBody,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
) -> InternalTestTopupConfirmed:
    """Шаг B: подтвердить через apply_payment_succeeded (идемпотентно)."""
    pr = await session.execute(select(Payment).where(Payment.id == payment_id))
    payment = pr.scalar_one_or_none()
    if payment is None:
        raise HTTPException(status_code=404, detail="Платёж не найден")

    if payment.provider != PaymentProvider.mock:
        raise HTTPException(
            status_code=400,
            detail="Эндпоинт только для тестовых платежей с provider=mock",
        )

    already_succeeded = payment.status == PaymentStatus.succeeded

    payload = body.raw_payload if body.raw_payload is not None else {}
    merged = {"source": "internal_wallet_test", **payload}

    try:
        await apply_payment_succeeded(session, payment_id, raw_payload=merged)
    except SettlementError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    await session.refresh(payment)
    bal = await session.execute(
        select(User.balance_cents).where(User.id == payment.user_id)
    )
    balance_cents = bal.scalar_one()

    return InternalTestTopupConfirmed(
        payment_id=payment.id,
        status=payment.status.value,
        user_balance_cents=balance_cents,
        already_succeeded_before_call=already_succeeded,
    )
