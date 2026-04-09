from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import OrderStatus
from app.schemas.seo import SeoOrderConfigSchema


class OrderQuotePreview(BaseModel):
    """Быстрый пересчёт цены по счётчику слов и пресету голоса."""

    target_word_count: int = Field(ge=300, le=15000)
    brand_voice_id: str = Field(min_length=1, max_length=64)


class OrderCreateRequest(BaseModel):
    brand_name: str = Field(min_length=1, max_length=256)
    task_notes: str | None = Field(default=None, max_length=8000)
    keywords: list[str] = Field(min_length=1, max_length=50)
    lsi_keywords: list[str] = Field(default_factory=list, max_length=80)
    target_word_count: int = Field(ge=300, le=15000)
    brand_voice_id: str = Field(min_length=1, max_length=64)
    seo: SeoOrderConfigSchema


class OrderResponse(BaseModel):
    id: int
    status: OrderStatus
    brand_name: str
    task_notes: str | None
    keywords: list[str]
    lsi_keywords: list[str]
    seo_config: dict
    target_word_count: int
    price_base_cents: int
    discount_cents: int
    price_cents: int
    brand_voice_id: str
    generated_text: str | None
    generated_asset_uri: str | None
    moderated_at: datetime | None = None
    moderated_by_user_id: int | None = None
    moderation_notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OrderQuoteResponse(BaseModel):
    target_word_count: int
    price_base_cents: int
    discount_cents: int
    price_cents: int
    currency: str = "RUB"
    first_order_bonus_applied: bool = False


class OrderPayResponse(BaseModel):
    order: OrderResponse
    user_balance_cents: int


class OrderGenerateResponse(BaseModel):
    order: OrderResponse
