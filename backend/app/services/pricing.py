from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import datetime, timezone

from app.models.enums import OrderKind
from app.models.user import User

PRICE_PER_WORD_CENTS = 70  # 0.7 RUB/word
FIRST_ORDER_BONUS_PERCENT = 30
# Уникализация: ниже полной генерации, но с тем же минимумом по «весу» исходника.
UNIQUIFY_PRICE_FACTOR = 0.65
MIN_BILLING_WORDS = 300
MAX_BILLING_WORDS = 15000


def count_words_text(text: str) -> int:
    """Грубый подсчёт слов/токенов (латиница/кириллица, дефисы внутри слова)."""
    if not text or not str(text).strip():
        return 0
    return len(re.findall(r"\S+", str(text).strip()))


def billable_words_uniquify(source_text: str) -> int:
    """База для тарифа уникализации: max(источник, 300), не выше потолка."""
    w = count_words_text(source_text)
    return min(MAX_BILLING_WORDS, max(MIN_BILLING_WORDS, w))


@dataclass(slots=True, frozen=True)
class OrderPriceBreakdown:
    price_base_cents: int
    discount_cents: int
    price_cents: int
    bonus_applied: bool
    # uniquify: слова исходника в базе тарифа; generate: None
    billing_word_count: int | None = None


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


def calculate_order_price(
    user: User,
    target_word_count: int,
    *,
    order_kind: OrderKind = OrderKind.generate,
    source_text: str | None = None,
) -> OrderPriceBreakdown:
    billing_word_count: int | None = None
    if order_kind == OrderKind.uniquify:
        if not source_text or not str(source_text).strip():
            return OrderPriceBreakdown(
                price_base_cents=0,
                discount_cents=0,
                price_cents=0,
                bonus_applied=False,
                billing_word_count=None,
            )
        billing_word_count = billable_words_uniquify(source_text)
        price_base_cents = math.ceil(
            billing_word_count * PRICE_PER_WORD_CENTS * UNIQUIFY_PRICE_FACTOR
        )
    else:
        if target_word_count <= 0:
            return OrderPriceBreakdown(
                price_base_cents=0,
                discount_cents=0,
                price_cents=0,
                bonus_applied=False,
                billing_word_count=None,
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
        billing_word_count=billing_word_count,
    )


def quote_price_cents(
    target_word_count: int,
    *,
    order_kind: OrderKind = OrderKind.generate,
    source_text: str | None = None,
) -> tuple[int, int | None]:
    """
    Гостевой превью без скидок: (цена в копейках, billing_word_count для uniquify).
    """
    if order_kind == OrderKind.uniquify:
        if not source_text or not str(source_text).strip():
            return 0, None
        bw = billable_words_uniquify(source_text)
        return math.ceil(bw * PRICE_PER_WORD_CENTS * UNIQUIFY_PRICE_FACTOR), bw
    if target_word_count <= 0:
        return 0, None
    return target_word_count * PRICE_PER_WORD_CENTS, None
