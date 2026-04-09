"""Минимальные проверки денежного слоя (без интеграции с БД)."""

from app.services.payments.settlement import ledger_idempotency_key_for_payment


def test_ledger_idempotency_key_stable() -> None:
    assert ledger_idempotency_key_for_payment(1) == "payment_succeeded:1"
    assert ledger_idempotency_key_for_payment(42) == "payment_succeeded:42"
