"""
Серверная проверка email (синтаксис + при включённой настройке DNS MX/A).

Важно: подделка тел запросов в DevTools не устраняется «на фронте» — все решения
принимает только бэкенд (Pydantic, права по JWT, пересчёт цен на сервере).
"""

from __future__ import annotations

from email_validator import EmailNotValidError, validate_email

from app.config import settings

_ERR_RU = (
    "Похоже, опечатка в домене или такого ящика не существует. "
    "Проверь адрес — часто путают .ru и .com."
)


def ensure_deliverable_email(addr: str) -> str:
    """Возвращает нормализованный email; при ошибке — ValueError для Pydantic."""
    try:
        r = validate_email(
            addr.strip(),
            check_deliverability=settings.email_check_deliverability,
            allow_smtputf8=True,
        )
        return r.normalized
    except EmailNotValidError:
        raise ValueError(_ERR_RU) from None
