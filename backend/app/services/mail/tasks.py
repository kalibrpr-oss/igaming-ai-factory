"""Задачи отправки письма с кодом верификации."""

from __future__ import annotations

import logging

from app.config import settings
from app.services.mail.factory import get_email_sender

logger = logging.getLogger(__name__)


async def send_verification_email_task(
    to_email: str,
    username: str,
    raw_token: str,
    resend_count: int,
) -> None:
    transport = (settings.mail_transport or "logging").lower().strip()
    if transport == "logging":
        # Только при mail_transport=logging: удобный dev-просмотр кода (не для SMTP/prod-логов)
        logger.info(
            "verification email task: start to=%s resend_count=%s code=%s",
            to_email,
            resend_count,
            raw_token,
        )
    else:
        logger.info(
            "verification email task: start to=%s resend_count=%s (код не логируем)",
            to_email,
            resend_count,
        )
    sender = get_email_sender()
    await sender.send_email_verification(
        to_email=to_email,
        username=username,
        raw_token=raw_token,
        resend_count=resend_count,
    )


async def send_verification_email_task_safe(
    to_email: str,
    username: str,
    raw_token: str,
    resend_count: int,
) -> None:
    """Фоновая доставка для register: логируем сбой, но не ломаем уже созданный pending-account."""
    try:
        await send_verification_email_task(
            to_email=to_email,
            username=username,
            raw_token=raw_token,
            resend_count=resend_count,
        )
    except Exception:
        logger.exception(
            "verification email background send failed: to=%s resend_count=%s",
            to_email,
            resend_count,
        )
