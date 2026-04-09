"""Пополнение баланса (публичные схемы)."""

from pydantic import BaseModel, Field


class UserMockTopupBody(BaseModel):
    """Тестовое пополнение — только при enable_user_wallet_mock_topup."""

    amount_cents: int = Field(
        ...,
        ge=100,
        le=100_000_000,
        description="Сумма в копейках (мин. 1 ₽, макс. 1 000 000 ₽)",
    )


class UserMockTopupResponse(BaseModel):
    payment_id: int
    user_balance_cents: int
