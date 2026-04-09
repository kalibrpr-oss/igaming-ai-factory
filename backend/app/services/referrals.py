"""
Реферальная программа: коды, привязка, начисления рефереру при пополнении реферала.
Спека: Docs/spec-economy-referral-admin.md
"""

from __future__ import annotations

import re
import secrets

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import (
    BalanceReferenceType,
    BalanceTransactionType,
    PaymentKind,
    PaymentStatus,
)
from app.models.payment import Payment
from app.models.user import User

# Зарезервированы под роуты и служебное
_RESERVED_SLUGS = frozenset(
    {
        "api",
        "admin",
        "login",
        "register",
        "order",
        "orders",
        "dashboard",
        "wallet",
        "verify",
        "guide",
        "terms",
        "r",
        "ref",
        "www",
        "mail",
        "ftp",
        "static",
        "assets",
        "_next",
    }
)

_SLUG_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9-]{2,30})[a-z0-9]$|^[a-z0-9]{4}$")


def normalize_invite_code(raw: str | None) -> str | None:
    if raw is None:
        return None
    s = raw.strip().lower()
    return s or None


def validate_custom_referral_slug(code: str) -> str | None:
    """
    Возвращает текст ошибки для пользователя или None если ок.
    """
    c = code.strip().lower()
    if len(c) < 4 or len(c) > 32:
        return "Код: от 4 до 32 символов."
    if not _SLUG_PATTERN.fullmatch(c):
        return "Только латиница, цифры и дефис; не начинать/не заканчивать дефисом."
    if c in _RESERVED_SLUGS:
        return "Такой код зарезервирован. Выбери другой."
    return None


async def resolve_referrer_user_id(
    session: AsyncSession,
    invite_code: str | None,
) -> int | None:
    code = normalize_invite_code(invite_code)
    if not code:
        return None
    uid = await session.scalar(select(User.id).where(User.referral_code == code))
    return int(uid) if uid is not None else None


async def assign_unique_referral_code(session: AsyncSession, user: User) -> str:
    """Выдаёт пользователю уникальный referral_code (если ещё пусто)."""
    if user.referral_code:
        return user.referral_code
    for _ in range(48):
        cand = secrets.token_hex(5)  # 10 hex chars
        exists = await session.scalar(
            select(User.id).where(User.referral_code == cand)
        )
        if exists is None:
            user.referral_code = cand
            await session.flush()
            return cand
    raise RuntimeError("Не удалось сгенерировать уникальный реферальный код")


async def apply_referrer_reward_on_referee_topup(
    session: AsyncSession,
    referee_topup_payment: Payment,
) -> None:
    """
    После успешного wallet_topup реферала: бонус рефереру 50% первого пополнения,
    далее 15%. Идемпотентно по ключу referral_reward_topup:{payment_id}.
    """
    from app.models.balance_transaction import BalanceTransaction

    if referee_topup_payment.kind != PaymentKind.wallet_topup:
        return
    if referee_topup_payment.status != PaymentStatus.succeeded:
        return

    referee = await session.get(User, referee_topup_payment.user_id)
    if referee is None:
        return

    referrer_id = referee.referrer_user_id
    if referrer_id is None or referrer_id == referee.id:
        return

    idem = f"referral_reward_topup:{referee_topup_payment.id}"
    dup = await session.scalar(
        select(BalanceTransaction.id).where(BalanceTransaction.idempotency_key == idem)
    )
    if dup is not None:
        return

    res = await session.execute(
        select(User).where(User.id == referrer_id).with_for_update()
    )
    ref_user = res.scalar_one_or_none()
    if ref_user is None or not ref_user.is_active:
        return

    prior_topups = await session.scalar(
        select(func.count())
        .select_from(Payment)
        .where(
            Payment.user_id == referee.id,
            Payment.kind == PaymentKind.wallet_topup,
            Payment.status == PaymentStatus.succeeded,
            Payment.id != referee_topup_payment.id,
        )
    )
    is_first = (prior_topups or 0) == 0
    rate = 0.50 if is_first else 0.15
    reward = int(referee_topup_payment.amount_cents * rate)
    if reward < 1:
        return

    bt = BalanceTransaction(
        user_id=referrer_id,
        amount_cents=reward,
        type=BalanceTransactionType.referral_reward,
        reference_type=BalanceReferenceType.payment,
        reference_id=referee_topup_payment.id,
        idempotency_key=idem,
    )
    session.add(bt)
    ref_user.balance_cents = ref_user.balance_cents + reward
    await session.flush()
