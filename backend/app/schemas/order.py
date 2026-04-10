from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.models.enums import OrderKind, OrderStatus
from app.schemas.seo import SeoOrderConfigSchema
from app.services.pricing import count_words_text

SOURCE_TEXT_MAX_LEN = 120_000
UNIQUIFY_MIN_WORDS = 80


class OrderQuotePreview(BaseModel):
    """Быстрый пересчёт цены: генерация по целевому объёму или уникализация по исходнику."""

    order_kind: OrderKind = OrderKind.generate
    target_word_count: int = Field(ge=300, le=15000)
    brand_voice_id: str = Field(min_length=1, max_length=64)
    source_text: str | None = Field(default=None, max_length=SOURCE_TEXT_MAX_LEN)

    @model_validator(mode="after")
    def _validate_uniquify_preview(self) -> OrderQuotePreview:
        if self.order_kind == OrderKind.uniquify:
            st = (self.source_text or "").strip()
            if not st:
                raise ValueError("Для превью уникализации вставь исходный текст.")
            if count_words_text(st) < UNIQUIFY_MIN_WORDS:
                raise ValueError(f"Минимум {UNIQUIFY_MIN_WORDS} слов в исходнике.")
        return self


class OrderCreateRequest(BaseModel):
    order_kind: OrderKind = OrderKind.generate
    brand_name: str = Field(min_length=1, max_length=256)
    task_notes: str | None = Field(default=None, max_length=8000)
    keywords: list[str] = Field(min_length=1, max_length=50)
    lsi_keywords: list[str] = Field(default_factory=list, max_length=80)
    target_word_count: int = Field(ge=300, le=15000)
    brand_voice_id: str = Field(min_length=1, max_length=64)
    seo: SeoOrderConfigSchema
    source_text: str | None = Field(default=None, max_length=SOURCE_TEXT_MAX_LEN)

    @model_validator(mode="after")
    def _validate_uniquify_create(self) -> OrderCreateRequest:
        if self.order_kind == OrderKind.uniquify:
            st = (self.source_text or "").strip()
            if not st:
                raise ValueError("Для уникализации нужен исходный текст.")
            if count_words_text(st) < UNIQUIFY_MIN_WORDS:
                raise ValueError(f"Минимум {UNIQUIFY_MIN_WORDS} слов в исходнике.")
        return self


class OrderResponse(BaseModel):
    id: int
    status: OrderStatus
    order_kind: OrderKind = OrderKind.generate
    brand_name: str
    task_notes: str | None
    source_text: str | None = None
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
    order_kind: OrderKind = OrderKind.generate
    target_word_count: int
    billing_word_count: int | None = None
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
