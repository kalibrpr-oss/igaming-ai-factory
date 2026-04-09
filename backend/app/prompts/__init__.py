"""
Промпты для Claude: Brand Voice (voices/), системные слои (system/),
шаблоны генерации (generators/), второй проход (rewriters/).
"""

from app.prompts.context_factory import from_create_request, from_order_model
from app.prompts.registry import get_voice, list_brand_voices_meta
from app.prompts.types import GenerationContext

__all__ = [
    "GenerationContext",
    "from_create_request",
    "from_order_model",
    "get_voice",
    "list_brand_voices_meta",
]
