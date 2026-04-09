"""Схемы внутреннего тестового контура пополнения (не прод)."""

from pydantic import BaseModel, Field


class InternalTestTopupCreate(BaseModel):
    user_id: int = Field(..., ge=1)
    amount_cents: int = Field(..., gt=0)


class InternalTestTopupCreated(BaseModel):
    payment_id: int
    user_id: int
    amount_cents: int
    provider: str
    kind: str
    status: str
    external_id: str


class InternalTestTopupConfirmBody(BaseModel):
    raw_payload: dict | None = Field(
        default=None,
        description="Произвольный JSON для raw_payload платежа (имитация webhook)",
    )


class InternalTestTopupConfirmed(BaseModel):
    payment_id: int
    status: str
    user_balance_cents: int
    already_succeeded_before_call: bool = Field(
        description="True, если платёж уже был succeeded до этого запроса (идемпотентный no-op)"
    )
