import math
from datetime import datetime, timedelta, timezone

from app.models.enums import OrderKind
from app.models.user import User
from app.services.orders.payment import ledger_idempotency_key_for_order
from app.services.pricing import (
    PRICE_PER_WORD_CENTS,
    UNIQUIFY_PRICE_FACTOR,
    calculate_order_price,
    count_words_text,
)


def test_calculate_order_price_without_bonus_when_consumed() -> None:
    user = User(
        email="u@example.com",
        username="u1",
        hashed_password="x",
        first_order_bonus_expires_at=None,
        first_order_bonus_consumed_at=datetime.now(timezone.utc),
    )
    result = calculate_order_price(user, 1000)
    assert result.price_base_cents == 70000
    assert result.discount_cents == 0
    assert result.price_cents == 70000
    assert result.bonus_applied is False


def test_calculate_order_price_bonus_when_no_expiry() -> None:
    """По умолчанию скидка 30% на первый заказ, пока не оплатили со скидкой."""
    user = User(
        email="u0@example.com",
        username="u0",
        hashed_password="x",
        first_order_bonus_expires_at=None,
        first_order_bonus_consumed_at=None,
    )
    result = calculate_order_price(user, 1000)
    assert result.discount_cents == 21000
    assert result.price_cents == 49000
    assert result.bonus_applied is True


def test_calculate_order_price_without_bonus_when_expired() -> None:
    user = User(
        email="ue@example.com",
        username="ue",
        hashed_password="x",
        first_order_bonus_expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        first_order_bonus_consumed_at=None,
    )
    result = calculate_order_price(user, 500)
    assert result.discount_cents == 0
    assert result.bonus_applied is False


def test_calculate_order_price_with_bonus() -> None:
    user = User(
        email="u2@example.com",
        username="u2",
        hashed_password="x",
        first_order_bonus_expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        first_order_bonus_consumed_at=None,
    )
    result = calculate_order_price(user, 1000)
    assert result.price_base_cents == 70000
    assert result.discount_cents == 21000
    assert result.price_cents == 49000
    assert result.bonus_applied is True


def test_order_debit_idempotency_key() -> None:
    assert ledger_idempotency_key_for_order(42) == "order_debit:42"


def test_uniquify_price_lower_than_generate_same_billable_words() -> None:
    user = User(
        email="uq@example.com",
        username="uq",
        hashed_password="x",
        first_order_bonus_expires_at=None,
        first_order_bonus_consumed_at=datetime.now(timezone.utc),
    )
    words = " ".join([f"w{i}" for i in range(500)])
    assert count_words_text(words) == 500
    gen = calculate_order_price(user, 500, order_kind=OrderKind.generate)
    uniq = calculate_order_price(
        user, 1500, order_kind=OrderKind.uniquify, source_text=words
    )
    assert uniq.billing_word_count == 500
    assert uniq.price_base_cents < gen.price_base_cents
    assert uniq.price_base_cents == math.ceil(
        500 * PRICE_PER_WORD_CENTS * UNIQUIFY_PRICE_FACTOR
    )


def test_uniquify_min_billing_floor_300_words() -> None:
    user = User(
        email="um@example.com",
        username="um",
        hashed_password="x",
        first_order_bonus_consumed_at=datetime.now(timezone.utc),
    )
    short = " ".join([f"x{i}" for i in range(100)])
    r = calculate_order_price(
        user, 800, order_kind=OrderKind.uniquify, source_text=short
    )
    assert r.billing_word_count == 300
