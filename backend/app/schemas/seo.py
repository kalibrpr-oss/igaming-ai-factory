from typing import Literal

from pydantic import BaseModel, Field


class SeoOrderConfigSchema(BaseModel):
    """Поля из Docs/seo-order-spec.md — валидация до сохранения в JSONB."""

    language: str = Field(default="ru", min_length=2, max_length=8)
    primary_keyword: str = Field(min_length=1, max_length=256)
    keyword_density_percent: float = Field(ge=0.5, le=3.0, default=1.5)
    heading_format: Literal[
        "strict_h1_h2_h3",
        "flat_h2_only",
        "review_blocks",
    ] = "strict_h1_h2_h3"
    meta_description_length: int = Field(ge=120, le=200, default=160)
    article_type: Literal["review", "comparison", "guide", "bonus", "news"] = "review"
    include_faq_block: bool = True
    include_table_compare: bool = False
    canonical_url_hint: str | None = Field(default=None, max_length=512)
