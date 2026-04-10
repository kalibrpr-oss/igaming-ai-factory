"""
Пользовательский промпт (generation): передача темы, ключей, LSI и SEO-параметров в LLM.
"""

from app.prompts.generators.russian_hints import russian_editor_hints_block
from app.prompts.types import GenerationContext


def _fmt_list(items: list[str], empty: str) -> str:
    if not items:
        return empty
    return "\n".join(f"- {x.strip()}" for x in items if x and x.strip())


def _voice_reminder(voice_id: str) -> str:
    if voice_id == "bold_daring":
        return (
            "\nАктивный Brand Voice: Aggressive — не пиши нейтральным обзорчиком; "
            "держи рубленый, уверенный тон с иронией (см. system).\n"
        )
    if voice_id == "expert_precise":
        return "\nАктивный Brand Voice: Expert — сухая точность, без сленга и лишней эмоции.\n"
    if voice_id == "friendly_warm":
        return "\nАктивный Brand Voice: Friendly — тепло и по-человечески, без агрессии.\n"
    return ""


def build_generation_user_message(ctx: GenerationContext) -> str:
    """Единый блок инструкций для шага generate_text."""
    seo = ctx.seo
    notes = (ctx.task_notes or "").strip()
    notes_block = f"\n\nДополнительно от заказчика:\n{notes}" if notes else ""

    order_hint = ""
    if ctx.order_id is not None:
        order_hint = (
            f"\nИдентификатор заказа (для уникальности формулировок, не включать в текст): {ctx.order_id}\n"
        )

    # Коридор слов: основной текст = всё до отдельной строки «Meta:» (заголовки ## входят в подсчёт).
    tw = ctx.target_word_count
    lo = max(300, int(tw * 0.92))
    hi = int(tw * 1.08)

    ru_block = ""
    if (seo.language or "").lower().startswith("ru"):
        ru_block = "\n" + russian_editor_hints_block() + "\n"

    return f"""Напиши SEO-статью для гемблинга по следующему ТЗ.

Бренд / проект: {ctx.brand_name.strip()}
Целевой объём (ОБЯЗАТЕЛЬНО): {tw} слов по основному тексту.
Под основным текстом понимается всё до отдельной финальной строки, начинающейся с «Meta:» (её в подсчёт НЕ включай).
Допустимый коридор: {lo}–{hi} слов. Нельзя выходить за верхнюю границу без крайней необходимости; лучше чуть короче, чем заметно длиннее.
{_voice_reminder(ctx.brand_voice_id)}

Ключевые фразы (использовать естественно, без переспама):
{_fmt_list(ctx.keywords, "(не задано)")}

LSI и смежная семантика:
{_fmt_list(ctx.lsi_keywords, "(не задано)")}

Параметры SEO:
- язык контента: {seo.language}
- главный ключ для плотности и заголовков: {seo.primary_keyword}
- ориентир плотности главного ключа: ~{seo.keyword_density_percent}% (без искусственной набивки)
- структура заголовков: {seo.heading_format}
- длина meta description (символов, ориентир): ~{seo.meta_description_length}
- тип статьи: {seo.article_type}
- блок FAQ: {"да" if seo.include_faq_block else "нет"}
- таблица сравнения: {"да" if seo.include_table_compare else "нет"}
- подсказка canonical URL (если уместно упомянуть): {seo.canonical_url_hint or "не задана"}
{order_hint}{notes_block}{ru_block}
Формат выхода:
- полный текст статьи с заголовками по выбранной структуре
- в конце отдельной строкей Meta: … (одна строка мета-описания заданной длины)
- без предисловий от модели и без Markdown-ограждений вокруг всего текста, если не просили иное в голосе
""".strip()
