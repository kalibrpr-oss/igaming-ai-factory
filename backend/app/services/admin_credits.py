"""Ручная выдача Credits админом (проводка adjustment + note)."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.balance_transaction import BalanceTransaction
from app.models.enums import BalanceReferenceType, BalanceTransactionType
from app.models.user import User


class AdminCreditsError(Exception):
    """Ошибка выдачи (не HTTP)."""


async def grant_credits_by_admin(
    session: AsyncSession,
    *,
    target_user_id: int,
    amount_cents: int,
    admin_user_id: int,
    reason: str,
) -> tuple[BalanceTransaction, int]:
    if amount_cents <= 0:
        raise AdminCreditsError("Сумма должна быть положительной")
    trimmed = reason.strip()
    if not trimmed:
        raise AdminCreditsError("Укажите причину выдачи")

    stmt = select(User).where(User.id == target_user_id).with_for_update()
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise AdminCreditsError("Пользователь не найден")

    idem = f"admin_grant:{target_user_id}:{uuid.uuid4().hex}"
    if len(idem) > 128:
        idem = idem[:128]

    bt = BalanceTransaction(
        user_id=target_user_id,
        amount_cents=amount_cents,
        type=BalanceTransactionType.adjustment,
        reference_type=BalanceReferenceType.manual,
        reference_id=admin_user_id,
        idempotency_key=idem,
        note=trimmed[:512],
    )
    session.add(bt)
    user.balance_cents = user.balance_cents + amount_cents
    await session.flush()
    await session.refresh(bt)
    return bt, user.balance_cents
