"""Заглушка: письмо не уходит в сеть, текст доступен в DEBUG-логах."""

from __future__ import annotations

import logging

from app.services.mail.content import build_verification_email_text

logger = logging.getLogger(__name__)


class LoggingEmailSender:
    async def send_email_verification(
        self,
        *,
        to_email: str,
        username: str,
        raw_token: str,
        resend_count: int,
    ) -> None:
        body = build_verification_email_text(
            username=username,
            raw_token=raw_token,
            resend_count=resend_count,
        )
        logger.info(
            "email send (logging, no SMTP): start to=%s resend_count=%s code=%s",
            to_email,
            resend_count,
            raw_token,
        )
        logger.info("email send (logging): success to=%s", to_email)
        logger.debug("Текст письма (только DEBUG):\n%s", body)
