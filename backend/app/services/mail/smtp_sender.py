"""Отправка писем через SMTP (STARTTLS, Mail.ru и аналоги)."""

from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from functools import partial

import anyio

from app.config import settings
from app.services.mail.content import build_verification_email_text

logger = logging.getLogger(__name__)


def _send_verification_email_sync(
    *,
    host: str,
    port: int,
    smtp_user: str,
    smtp_password: str,
    from_email: str,
    from_name: str,
    to_email: str,
    subject: str,
    body: str,
) -> None:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = (
        formataddr((from_name, from_email)) if from_name.strip() else from_email
    )
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP(host, port, timeout=30) as smtp:
        smtp.starttls()
        smtp.login(smtp_user, smtp_password)
        smtp.send_message(msg)


class SmtpEmailSender:
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
        from_email = (settings.mail_from_email or settings.mail_from_address).strip()
        from_name = settings.mail_from_name.strip()

        logger.info(
            "SMTP send start: to=%s resend_count=%s",
            to_email,
            resend_count,
        )

        try:
            await anyio.to_thread.run_sync(
                partial(
                    _send_verification_email_sync,
                    host=settings.smtp_host,
                    port=settings.smtp_port,
                    smtp_user=settings.smtp_user,
                    smtp_password=settings.smtp_password,
                    from_email=from_email,
                    from_name=from_name,
                    to_email=to_email,
                    subject="Подтверждение email",
                    body=body,
                )
            )
        except Exception as exc:
            logger.error(
                "SMTP send failed: to=%s reason=%s",
                to_email,
                exc,
                exc_info=logger.isEnabledFor(logging.DEBUG),
            )
            # Пробрасываем — register/resend откатят транзакцию, не маскируя сбой как успех
            raise

        logger.info("SMTP send success: to=%s", to_email)
