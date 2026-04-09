"""Типы входных данных для генерации SEO-текстов."""

from dataclasses import dataclass

from app.schemas.seo import SeoOrderConfigSchema


@dataclass
class GenerationContext:
    """Полное ТЗ для пайплайна generate → rewrite."""

    brand_name: str
    keywords: list[str]
    lsi_keywords: list[str]
    task_notes: str | None
    target_word_count: int
    brand_voice_id: str
    seo: SeoOrderConfigSchema
    """Опционально: уникальный идентификатор заказа для логов и вариативности формулировок в промпте."""
    order_id: int | None = None
