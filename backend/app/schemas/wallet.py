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


class YooKassaTopupCreateBody(BaseModel):
    """Создание платежа ЮKassa (редирект на оплату)."""

    amount_cents: int = Field(
        ...,
        ge=100,
        le=100_000_000,
        description="Сумма в копейках",
    )


class YooKassaTopupCreatedResponse(BaseModel):
    payment_id: int
    confirmation_url: str


class YooKassaStatusResponse(BaseModel):
    yookassa_topup_available: bool
