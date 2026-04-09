"""Сборка GenerationContext из API и моделей заказа."""

from app.models.order import Order
from app.prompts.types import GenerationContext
from app.schemas.order import OrderCreateRequest
from app.schemas.seo import SeoOrderConfigSchema


def from_create_request(
    body: OrderCreateRequest,
    *,
    order_id: int | None = None,
) -> GenerationContext:
    """Контекст для пайплайна из тела создания заказа."""
    return GenerationContext(
        brand_name=body.brand_name.strip(),
        keywords=list(body.keywords),
        lsi_keywords=list(body.lsi_keywords),
        task_notes=body.task_notes,
        target_word_count=body.target_word_count,
        brand_voice_id=body.brand_voice_id,
        seo=body.seo,
        order_id=order_id,
    )


def from_order_model(order: Order) -> GenerationContext:
    """Контекст из сохранённой сущности Order (после оплаты / в воркере)."""
    seo = SeoOrderConfigSchema.model_validate(order.seo_config)
    return GenerationContext(
        brand_name=order.brand_name,
        keywords=[str(k) for k in (order.keywords or [])],
        lsi_keywords=[str(k) for k in (order.lsi_keywords or [])],
        task_notes=order.task_notes,
        target_word_count=order.target_word_count,
        brand_voice_id=order.brand_voice_id,
        seo=seo,
        order_id=order.id,
    )
