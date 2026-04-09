"""Фабрика отправителя по настройкам."""

from __future__ import annotations

from app.config import settings
from app.services.mail.logging_sender import LoggingEmailSender
from app.services.mail.protocol import EmailSender
from app.services.mail.smtp_sender import SmtpEmailSender


def get_email_sender() -> EmailSender:
    transport = (settings.mail_transport or "logging").lower().strip()
    if transport == "logging":
        return LoggingEmailSender()
    if transport == "smtp":
        return SmtpEmailSender()
    raise ValueError(f"Неизвестный mail_transport: {settings.mail_transport!r}")
