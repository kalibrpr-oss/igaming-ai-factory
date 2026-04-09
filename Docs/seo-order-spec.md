# Технические поля заказа SEO-статьи (iGaming)

Используются в `Order.seo_config` и форме заказа.

| Поле | Назначение |
|------|------------|
| `language` | Язык текста (ISO 639-1): `ru`, `en`, … |
| `primary_keyword` | Главный ключ для плотности и H1 |
| `keyword_density_percent` | Целевая плотность основного ключа (0.5–3%) |
| `heading_format` | Структура: `strict_h1_h2_h3`, `flat_h2_only`, `review_blocks` |
| `meta_description_length` | Длина meta description (120–200 символов) |
| `article_type` | `review`, `comparison`, `guide`, `bonus`, `news` |
| `include_faq_block` | Блок FAQ (микроразметка) |
| `include_table_compare` | Таблица сравнения бонусов/параметров |
| `canonical_url_hint` | Подсказка для canonical (опционально) |

Ключи и LSI дублируются в списках `keywords` и `lsi_keywords` верхнего уровня заказа для валидации и промпта.
