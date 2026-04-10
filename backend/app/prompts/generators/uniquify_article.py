"""
Пользовательский промпт: уникализация готового текста под SEO и Brand Voice.
"""

from app.prompts.generators.russian_hints import russian_editor_hints_block
from app.prompts.generators.seo_article import _fmt_list, _voice_reminder
from app.prompts.types import GenerationContext


def build_uniquify_user_message(ctx: GenerationContext, source_text: str) -> str:
    """Переписать исходник: новая формулировка, те же факты, целевой объём и SEO."""
    seo = ctx.seo
    notes = (ctx.task_notes or "").strip()
    notes_block = f"\n\nДополнительно от заказчика:\n{notes}" if notes else ""

    order_hint = ""
    if ctx.order_id is not None:
        order_hint = (
            f"\nИдентификатор заказа (для вариативности, не включать в текст): {ctx.order_id}\n"
        )

    tw = ctx.target_word_count
    lo = max(300, int(tw * 0.92))
    hi = int(tw * 1.08)

    ru_block = ""
    if (seo.language or "").lower().startswith("ru"):
        ru_block = "\n" + russian_editor_hints_block() + "\n"

    src = source_text.strip()

    return f"""Задача: УНИКАЛИЗАЦИЯ статьи для гемблинга (не копировать формулировки и синтаксис исходника).

Ниже — ИСХОДНЫЙ текст заказчика. Перепиши его полностью: другие предложения, другой ритм и связки, но:
- сохрани факты: цифры, условия бонусов, сроки, названия игр/провайдеров, юридические формулировки — как в источнике; не выдумывай новых фактов
- если в исходнике явная ошибка — не «чинить» без указания в ТЗ; можно слегка смягчить формулировку, не меняя смысл
- выход должен соответствовать Brand Voice и SEO-параметрам ниже

Бренд / проект: {ctx.brand_name.strip()}
Целевой объём результата (ОБЯЗАТЕЛЬНО): {tw} слов по основному тексту.
Под основным текстом — всё до отдельной финальной строки «Meta:» (её в подсчёт не включать).
Допустимый коридор: {lo}–{hi} слов. Не раздувай сверх {hi}; лучше чуть короче, чем заметно длиннее.
{_voice_reminder(ctx.brand_voice_id)}

Ключевые фразы (естественно, без переспама):
{_fmt_list(ctx.keywords, "(не задано)")}

LSI и смежная семантика:
{_fmt_list(ctx.lsi_keywords, "(не задано)")}

Параметры SEO:
- язык контента: {seo.language}
- главный ключ: {seo.primary_keyword}
- ориентир плотности главного ключа: ~{seo.keyword_density_percent}%
- структура заголовков: {seo.heading_format}
- длина meta description (символов): ~{seo.meta_description_length}
- тип статьи: {seo.article_type}
- блок FAQ: {"да" if seo.include_faq_block else "нет"}
- таблица сравнения: {"да" if seo.include_table_compare else "нет"}
- подсказка canonical URL: {seo.canonical_url_hint or "не задана"}
{order_hint}{notes_block}{ru_block}
Формат выхода:
- полный текст с заголовками по выбранной структуре
- в конце отдельной строкой Meta: … (одна строка мета-описания)
- без предисловий модели и без Markdown-ограждений вокруг всего текста

--- ИСХОДНИК ЗАКАЗЧИКА ---

{src}
""".strip()
