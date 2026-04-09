"""Списание баланса за заказ через ledger (идемпотентно, атомарно)."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.balance_transaction import BalanceTransaction
from app.models.enums import BalanceReferenceType, BalanceTransactionType, OrderStatus
from app.models.order import Order
from app.models.user import User


class OrderPaymentError(Exception):
    """Ошибка бизнес-логики оплаты заказа из баланса."""


def ledger_idempotency_key_for_order(order_id: int) -> str:
    return f"order_debit:{order_id}"


async def apply_order_payment(session: AsyncSession, order_id: int) -> Order:
    """
    Пытается оплатить заказ из баланса пользователя.
    - idempotent: повторный вызов для paid — no-op
    - атомарно: баланс + ledger + статус заказа в одной транзакции
    """
    order_stmt = select(Order).where(Order.id == order_id).with_for_update()
    order = (await session.execute(order_stmt)).scalar_one_or_none()
    if order is None:
        raise OrderPaymentError(f"Заказ {order_id} не найден")

    if order.status == OrderStatus.paid:
        return order

    if order.price_cents <= 0:
        raise OrderPaymentError("Некорректная сумма заказа для списания")

    user_stmt = select(User).where(User.id == order.user_id).with_for_update()
    user = (await session.execute(user_stmt)).scalar_one_or_none()
    if user is None:
        raise OrderPaymentError(f"Пользователь {order.user_id} не найден")

    idem = ledger_idempotency_key_for_order(order.id)
    existing = await session.execute(
        select(BalanceTransaction.id).where(BalanceTransaction.idempotency_key == idem)
    )
    if existing.scalar_one_or_none() is not None:
        # Healing: если ledger уже есть, доводим статус заказа до paid.
        order.status = OrderStatus.paid
        if order.discount_cents > 0 and user.first_order_bonus_consumed_at is None:
            user.first_order_bonus_consumed_at = datetime.now(timezone.utc)
        await session.flush()
        return order

    if user.balance_cents < order.price_cents:
        raise OrderPaymentError("Недостаточно средств для оплаты заказа")

    debit = BalanceTransaction(
        user_id=user.id,
        amount_cents=-order.price_cents,
        type=BalanceTransactionType.order_debit,
        reference_type=BalanceReferenceType.order,
        reference_id=order.id,
        idempotency_key=idem,
    )
    session.add(debit)

    await session.execute(
        update(User)
        .where(User.id == user.id)
        .values(balance_cents=user.balance_cents - order.price_cents)
    )

    order.status = OrderStatus.paid
    if order.discount_cents > 0 and user.first_order_bonus_consumed_at is None:
        user.first_order_bonus_consumed_at = datetime.now(timezone.utc)

    await session.flush()
    return order
