"""
Единая точка зачисления по успешному платежу (идемпотентно, в транзакции сессии).
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.balance_transaction import BalanceTransaction
from app.models.enums import (
    BalanceReferenceType,
    BalanceTransactionType,
    PaymentKind,
    PaymentStatus,
)
from app.models.payment import Payment
from app.models.user import User


class SettlementError(Exception):
    """Ошибка бизнес-логики зачисления (не HTTP)."""


def ledger_idempotency_key_for_payment(payment_id: int) -> str:
    """Один ключ на успешное зачисление по платежу (топап)."""
    return f"payment_succeeded:{payment_id}"


async def apply_payment_succeeded(
    session: AsyncSession,
    payment_id: int,
    *,
    raw_payload: dict[str, Any] | None = None,
) -> Payment:
    """
    Переводит платёж в succeeded и при kind=wallet_topup создаёт проводку + увеличивает balance_cents.
    Повторный вызов для уже succeeded — no-op (баланс не дублируется).

    Для wallet_topup статус succeeded выставляется только после записи проводки и обновления баланса.
    """
    stmt = select(Payment).where(Payment.id == payment_id).with_for_update()
    result = await session.execute(stmt)
    payment = result.scalar_one_or_none()
    if payment is None:
        raise SettlementError(f"Платёж {payment_id} не найден")

    if payment.status == PaymentStatus.succeeded:
        return payment

    if payment.kind == PaymentKind.wallet_topup and payment.order_id is not None:
        raise SettlementError("wallet_topup не должен содержать order_id")

    if payment.kind == PaymentKind.order_payment:
        payment.status = PaymentStatus.succeeded
        if raw_payload is not None:
            payment.raw_payload = raw_payload
        await session.flush()
        return payment

    if payment.kind != PaymentKind.wallet_topup:
        raise SettlementError(f"Неизвестный kind платежа: {payment.kind}")

    if payment.amount_cents <= 0:
        raise SettlementError("Сумма пополнения должна быть положительной")

    idem = ledger_idempotency_key_for_payment(payment.id)

    existing = await session.execute(
        select(BalanceTransaction.id).where(BalanceTransaction.idempotency_key == idem)
    )
    if existing.scalar_one_or_none() is not None:
        payment.status = PaymentStatus.succeeded
        if raw_payload is not None:
            payment.raw_payload = raw_payload
        await session.flush()
        return payment

    u_stmt = select(User).where(User.id == payment.user_id).with_for_update()
    user = (await session.execute(u_stmt)).scalar_one_or_none()
    if user is None:
        raise SettlementError(f"Пользователь {payment.user_id} не найден")

    bt = BalanceTransaction(
        user_id=payment.user_id,
        amount_cents=payment.amount_cents,
        type=BalanceTransactionType.topup,
        reference_type=BalanceReferenceType.payment,
        reference_id=payment.id,
        idempotency_key=idem,
    )
    session.add(bt)

    await session.execute(
        update(User)
        .where(User.id == payment.user_id)
        .values(balance_cents=user.balance_cents + payment.amount_cents)
    )

    payment.status = PaymentStatus.succeeded
    if raw_payload is not None:
        payment.raw_payload = raw_payload

    await session.flush()

    from app.services.referrals import apply_referrer_reward_on_referee_topup

    await apply_referrer_reward_on_referee_topup(session, payment)

    return payment
