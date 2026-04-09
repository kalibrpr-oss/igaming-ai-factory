from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import OrderStatus


class AdminUserRow(BaseModel):
    id: int
    email: EmailStr
    username: str
    created_at: datetime
    is_active: bool
    is_admin: bool
    orders_total: int = 0
    payments_succeeded: int = 0

    model_config = {"from_attributes": True}


class AdminReviewOrderRow(BaseModel):
    id: int
    user_id: int
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
