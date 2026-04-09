"""Демо-переписывание короткого текста в выбранном Brand Voice (один вызов Claude)."""

import asyncio

from app.config import settings
from app.prompts.registry import get_voice
from app.prompts.system.assembler import assemble_generation_system_prompt
from app.services.llm.claude_client import call_claude_sync


def _rewrite_sync(text: str, voice_id: str) -> str:
    if not settings.anthropic_api_key.strip():
        raise RuntimeError("ANTHROPIC_API_KEY не задан в .env")

    voice = get_voice(voice_id)
    base = assemble_generation_system_prompt(voice)
    system = (
        f"{base}\n\n"
        "Задача: перепиши текст пользователя ниже, сохраняя смысл и факты. "
        "Объём примерно как у оригинала (ориентир ~50 слов, допускается небольшое отклонение). "
        "Не добавляй выдуманных данных. Выход — только переписанный текст, без преамбулы."
    )
    return call_claude_sync(
        system=system,
        user=f"Исходный текст:\n\n{text.strip()}",
        max_tokens=2048,
    )


async def rewrite_demo_text(text: str, voice_id: str) -> str:
    return await asyncio.to_thread(_rewrite_sync, text, voice_id)
