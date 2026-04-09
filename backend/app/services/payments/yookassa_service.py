"""
Обертка над официальным SDK ЮKassa (синхронные вызовы — вызывать из asyncio.to_thread).
"""

from __future__ import annotations

import logging
from typing import Any

from yookassa import Configuration, Payment

from app.config import settings

logger = logging.getLogger(__name__)


def _amount_str_from_cents(amount_cents: int) -> str:
    """ЮKassa: сумма в рублях, строка с двумя знаками после запятой."""
    return f"{amount_cents // 100}.{amount_cents % 100:02d}"


def _configure() -> None:
    if not settings.yookassa_shop_id or not settings.yookassa_secret_key:
        raise RuntimeError("ЮKassa не настроена (shop_id / secret_key)")
    Configuration.configure(settings.yookassa_shop_id, settings.yookassa_secret_key)


def sync_create_wallet_topup_payment(
    *,
    amount_cents: int,
    return_url: str,
    internal_payment_id: int,
    user_id: int,
) -> tuple[str, str]:
    """
    Создаёт платёж в ЮKassa. Возвращает (yookassa_payment_id, confirmation_url).
    """
    _configure()
    idempotency_key = f"wallet-topup-{internal_payment_id}"
    payload: dict[str, Any] = {
        "amount": {
            "value": _amount_str_from_cents(amount_cents),
            "currency": "RUB",
        },
        "confirmation": {
            "type": "redirect",
            "return_url": return_url,
        },
        "capture": True,
        "description": f"Пополнение баланса Conveer #{internal_payment_id}",
        "metadata": {
            "internal_payment_id": str(internal_payment_id),
            "user_id": str(user_id),
            "kind": "wallet_topup",
        },
    }
    resp = Payment.create(payload, idempotency_key)
    yid = resp.id
    conf = resp.confirmation
    if conf is None:
        raise RuntimeError("ЮKassa: нет confirmation в ответе")
    url = getattr(conf, "confirmation_url", None)
    if not url:
        raise RuntimeError("ЮKassa: нет confirmation_url")
    if not yid:
        raise RuntimeError("ЮKassa: нет id платежа")
    return str(yid), str(url)


def sync_fetch_payment(yookassa_payment_id: str) -> Any:
    """Проверка статуса платежа на стороне ЮKassa (защита от поддельного webhook)."""
    _configure()
    return Payment.find_one(yookassa_payment_id)
