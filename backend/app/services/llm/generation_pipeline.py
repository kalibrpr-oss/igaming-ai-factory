"""
Продакшн-пайплайн SEO-текста: generate_text → rewrite_text → финал.

Подключается к заказам после оплаты; демо использует только отдельный rewrite-demo endpoint.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from app.prompts.generators.seo_article import build_generation_user_message
from app.prompts.generators.uniquify_article import build_uniquify_user_message
from app.prompts.registry import get_voice
from app.prompts.rewriters.humanize import build_rewrite_user_message
from app.prompts.system.assembler import (
    assemble_generation_system_prompt,
    assemble_rewrite_system_prompt,
)
from app.prompts.types import GenerationContext
from app.services.llm.claude_client import call_claude_sync, estimate_max_tokens_for_words


@dataclass
class SeoGenerationResult:
    """draft — сырой выход шага 1; final — после rewrite."""

    draft_text: str
    final_text: str


def generate_text_sync(ctx: GenerationContext) -> str:
    """Шаг 1: первичная генерация по ТЗ."""
    voice = get_voice(ctx.brand_voice_id)
    system = assemble_generation_system_prompt(voice)
    user = build_generation_user_message(ctx)
    max_tokens = estimate_max_tokens_for_words(ctx.target_word_count)
    return call_claude_sync(system=system, user=user, max_tokens=max_tokens)


def uniquify_pass_sync(ctx: GenerationContext, source_text: str) -> str:
    """Шаг 1 для уникализации: глубокая переработка исходника под SEO и голос."""
    voice = get_voice(ctx.brand_voice_id)
    system = assemble_generation_system_prompt(voice)
    user = build_uniquify_user_message(ctx, source_text)
    max_tokens = estimate_max_tokens_for_words(ctx.target_word_count)
    return call_claude_sync(system=system, user=user, max_tokens=max_tokens)


def rewrite_text_sync(
    draft_text: str,
    voice_id: str,
    *,
    target_word_count: int,
    language: str,
) -> str:
    """Шаг 2: доводка черновика (тот же Brand Voice + слой rewrite)."""
    voice = get_voice(voice_id)
    system = assemble_rewrite_system_prompt(voice)
    user = build_rewrite_user_message(
        draft_text,
        target_word_count=target_word_count,
        language=language,
        voice_id=voice_id,
    )
    # Лимит от цели заказа (+запас под строку Meta:), не от раздутого черновика.
    max_tokens = estimate_max_tokens_for_words(int(target_word_count * 1.12))
    return call_claude_sync(system=system, user=user, max_tokens=max_tokens)


def run_seo_pipeline_sync(ctx: GenerationContext) -> SeoGenerationResult:
    """Синхронный полный прогон: generate → rewrite."""
    draft = generate_text_sync(ctx)
    final = rewrite_text_sync(
        draft,
        ctx.brand_voice_id,
        target_word_count=ctx.target_word_count,
        language=ctx.seo.language,
    )
    return SeoGenerationResult(draft_text=draft, final_text=final)


async def run_seo_pipeline_async(ctx: GenerationContext) -> SeoGenerationResult:
    """Асинхронная обёртка (не блокирует event loop)."""

    def _run() -> SeoGenerationResult:
        return run_seo_pipeline_sync(ctx)

    return await asyncio.to_thread(_run)


def run_uniquify_pipeline_sync(
    ctx: GenerationContext, source_text: str
) -> SeoGenerationResult:
    """Уникализация: переписывание исходника → тот же rewrite-проход, что и у генерации."""
    draft = uniquify_pass_sync(ctx, source_text)
    final = rewrite_text_sync(
        draft,
        ctx.brand_voice_id,
        target_word_count=ctx.target_word_count,
        language=ctx.seo.language,
    )
    return SeoGenerationResult(draft_text=draft, final_text=final)


async def run_uniquify_pipeline_async(
    ctx: GenerationContext, source_text: str
) -> SeoGenerationResult:
    def _run() -> SeoGenerationResult:
        return run_uniquify_pipeline_sync(ctx, source_text)

    return await asyncio.to_thread(_run)


async def generate_text_async(ctx: GenerationContext) -> str:
    return await asyncio.to_thread(generate_text_sync, ctx)


async def rewrite_text_async(
    draft_text: str,
    voice_id: str,
    *,
    target_word_count: int,
    language: str,
) -> str:
    return await asyncio.to_thread(
        rewrite_text_sync,
        draft_text,
        voice_id,
        target_word_count=target_word_count,
        language=language,
    )
