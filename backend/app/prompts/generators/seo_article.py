"""
Пользовательский промпт (generation): передача темы, ключей, LSI и SEO-параметров в LLM.
"""

from app.prompts.types import GenerationContext


def _fmt_list(items: list[str], empty: str) -> str:
    if not items:
        return empty
    return "\n".join(f"- {x.strip()}" for x in items if x and x.strip())


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

    return f"""Напиши SEO-статью для гемблинга по следующему ТЗ.

Бренд / проект: {ctx.brand_name.strip()}
Целевой объём: около {ctx.target_word_count} слов (допустимо отклонение ±10%, не выходи сильно за рамки).

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
{order_hint}{notes_block}

Формат выхода:
- полный текст статьи с заголовками по выбранной структуре
- в конце отдельной строкей Meta: … (одна строка мета-описания заданной длины)
- без предисловий от модели и без Markdown-ограждений вокруг всего текста, если не просили иное в голосе
""".strip()
