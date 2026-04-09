"""Слой системных промптов: Anti-AI, продакшн-правила, сборка финального system."""

from app.prompts.system.anti_ai import ANTI_AI_RULES_BLOCK
from app.prompts.system.assembler import (
    assemble_generation_system_prompt,
    assemble_rewrite_system_prompt,
)
from app.prompts.system.core_rules import (
    CLIENT_ORDER_RULES_BLOCK,
    CORE_PRODUCTION_RULES_BLOCK,
    ENERGY_TONE_RULES_BLOCK,
)

__all__ = [
    "ANTI_AI_RULES_BLOCK",
    "CLIENT_ORDER_RULES_BLOCK",
    "CORE_PRODUCTION_RULES_BLOCK",
    "ENERGY_TONE_RULES_BLOCK",
    "assemble_generation_system_prompt",
    "assemble_rewrite_system_prompt",
]
