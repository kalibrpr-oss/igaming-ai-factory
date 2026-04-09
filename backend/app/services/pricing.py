from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.models.user import User

PRICE_PER_WORD_CENTS = 70  # 0.7 RUB/word
FIRST_ORDER_BONUS_PERCENT = 30


@dataclass(slots=True, frozen=True)
class OrderPriceBreakdown:
    price_base_cents: int
    discount_cents: int
    price_cents: int
    bonus_applied: bool


def first_order_bonus_available(user: User) -> bool:
    """
    Скидка 30% на первый оплаченный заказ (пока не списали бонус).
    Если задан first_order_bonus_expires_at — действует только до этой даты.
    Если None — без дедлайна, пока не оплатили первый заказ со скидкой.
    """
    if user.first_order_bonus_consumed_at is not None:
        return False
    expires_at = user.first_order_bonus_expires_at
    if expires_at is None:
        return True
    exp = (
        expires_at.replace(tzinfo=timezone.utc)
        if expires_at.tzinfo is None
        else expires_at
    )
    return exp >= datetime.now(timezone.utc)


def calculate_order_price(user: User, target_word_count: int) -> OrderPriceBreakdown:
    if target_word_count <= 0:
        return OrderPriceBreakdown(
            price_base_cents=0,
            discount_cents=0,
            price_cents=0,
            bonus_applied=False,
        )

    price_base_cents = target_word_count * PRICE_PER_WORD_CENTS
    bonus_applied = first_order_bonus_available(user)
    discount_cents = (
        (price_base_cents * FIRST_ORDER_BONUS_PERCENT) // 100 if bonus_applied else 0
    )
    return OrderPriceBreakdown(
        price_base_cents=price_base_cents,
        discount_cents=discount_cents,
        price_cents=price_base_cents - discount_cents,
        bonus_applied=bonus_applied,
    )


def quote_price_cents(target_word_count: int) -> int:
    """Совместимость со старым API превью: без персональных скидок."""
    if target_word_count <= 0:
        return 0
    return target_word_count * PRICE_PER_WORD_CENTS
