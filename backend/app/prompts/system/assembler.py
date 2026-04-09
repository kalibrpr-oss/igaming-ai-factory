"""
Сборка многослойного system prompt для Claude.

Порядок слоёв:
1) Brand Voice
2) Продакшн-правила (качество текста)
3) ТЗ и объём (заказ)
4) Energy & tone (анти-уныние)
5) Anti-AI

Этап rewrite добавляет отдельный слой humanize поверх того же стека.
"""

from app.prompts.base import BrandVoicePrompt
from app.prompts.rewriters.humanize import REWRITE_PASS_INSTRUCTIONS
from app.prompts.system.anti_ai import ANTI_AI_RULES_BLOCK
from app.prompts.system.core_rules import (
    CLIENT_ORDER_RULES_BLOCK,
    CORE_PRODUCTION_RULES_BLOCK,
    ENERGY_TONE_RULES_BLOCK,
)


def _join_blocks(*parts: str) -> str:
    return "\n\n".join(p.strip() for p in parts if p and p.strip())


def assemble_generation_system_prompt(voice: BrandVoicePrompt) -> str:
    """System prompt для шага 1: первичная генерация SEO-текста."""
    return _join_blocks(
        voice.build_system_prompt(),
        CORE_PRODUCTION_RULES_BLOCK,
        CLIENT_ORDER_RULES_BLOCK,
        ENERGY_TONE_RULES_BLOCK,
        ANTI_AI_RULES_BLOCK,
    )


def assemble_rewrite_system_prompt(voice: BrandVoicePrompt) -> str:
    """System prompt для шага 2: доводка черновика до «человеческого» вида."""
    return _join_blocks(
        voice.build_system_prompt(),
        CORE_PRODUCTION_RULES_BLOCK,
        CLIENT_ORDER_RULES_BLOCK,
        ENERGY_TONE_RULES_BLOCK,
        ANTI_AI_RULES_BLOCK,
        REWRITE_PASS_INSTRUCTIONS,
    )
