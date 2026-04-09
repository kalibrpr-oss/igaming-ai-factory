"""Абстракция отправки писем (подмена реализацией SMTP/API)."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class EmailSender(Protocol):
    async def send_email_verification(
        self,
        *,
        to_email: str,
        username: str,
        raw_token: str,
        resend_count: int,
    ) -> None:
        """Отправка письма с 6-значным кодом; сырой код не логировать при SMTP (см. tasks/factory)."""
        ...
