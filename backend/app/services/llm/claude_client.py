"""Синхронный вызов Claude Messages API — общая точка для демо и продакшн-пайплайна."""

from anthropic import Anthropic

from app.config import settings


def call_claude_sync(
    *,
    system: str,
    user: str,
    max_tokens: int,
) -> str:
    if not settings.anthropic_api_key.strip():
        raise RuntimeError("ANTHROPIC_API_KEY не задан в .env")

    client = Anthropic(api_key=settings.anthropic_api_key)
    msg = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    parts: list[str] = []
    for block in msg.content:
        if block.type == "text":
            parts.append(block.text)
    if not parts:
        raise RuntimeError("Пустой ответ модели")
    return "\n".join(parts).strip()


def estimate_max_tokens_for_words(word_count: int) -> int:
    """Верхняя граница токенов под объём (русский текст + заголовки + meta)."""
    # грубая оценка: ~1.3 токена на слово для выхода + запас
    raw = int(word_count * 1.8) + 2048
    return min(8192, max(4096, raw))
