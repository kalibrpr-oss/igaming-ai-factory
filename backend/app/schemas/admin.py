from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import (
    OrderKind,
    OrderStatus,
    PaymentKind,
    PaymentProvider,
    PaymentStatus,
)


class AdminUserRow(BaseModel):
    id: int
    email: EmailStr
    username: str
    created_at: datetime
    is_active: bool
    is_admin: bool
    orders_total: int = 0
    payments_succeeded: int = 0
    last_seen_at: datetime | None = None
    last_device_kind: str = "unknown"

    model_config = {"from_attributes": True}


class AdminUserBrief(BaseModel):
    id: int
    email: EmailStr
    username: str


class AdminReferralInviteRow(BaseModel):
    id: int
    email: EmailStr
    username: str
    created_at: datetime


class AdminOrderBrief(BaseModel):
    id: int
    status: OrderStatus
    brand_name: str
    price_cents: int
    created_at: datetime


class AdminUserDetail(BaseModel):
    id: int
    email: EmailStr
    username: str
    created_at: datetime
    is_active: bool
    is_admin: bool
    is_email_verified: bool
    balance_cents: int
    referral_code: str | None
    referral_slug_locked: bool
    referrer: AdminUserBrief | None
    referrals: list[AdminReferralInviteRow]
    referral_rewards_total_cents: int
    orders: list[AdminOrderBrief]
    last_seen_at: datetime | None
    last_device_kind: str


class AdminUserPatchBody(BaseModel):
    is_active: bool


class AdminGrantCreditsBody(BaseModel):
    amount_cents: int = Field(gt=0, le=100_000_000)
    reason: str = Field(min_length=1, max_length=500)


class AdminGrantCreditsResponse(BaseModel):
    transaction_id: int
    new_balance_cents: int


class AdminPaymentRow(BaseModel):
    id: int
    user_id: int
    user_email: EmailStr
    user_username: str
    order_id: int | None
    kind: PaymentKind
    provider: PaymentProvider
    amount_cents: int
    currency: str
    status: PaymentStatus
    created_at: datetime


class AdminReviewOrderRow(BaseModel):
    id: int
    user_id: int
    order_kind: OrderKind = OrderKind.generate
    brand_name: str
    target_word_count: int
    price_cents: int
    status: OrderStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdminReviewNotesBody(BaseModel):
    """Комментарий модератора (опционально)."""

    notes: str | None = Field(default=None, max_length=8000)


class AdminReviewActionResponse(BaseModel):
    order_id: int
    status: OrderStatus
    moderated_at: datetime
    moderation_notes: str | None
