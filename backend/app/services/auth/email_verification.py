"""Выпуск и проверка кодов подтверждения email (без отправки писем)."""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from app.models.email_verification_token import EmailVerificationToken
from app.models.enums import EmailVerificationPurpose

# TTL одноразового кода (15 минут)
TOKEN_TTL_SECONDS = 15 * 60

# Максимум выпусков кода verify_email за скользящие 24 ч (регистрация + resend + повторная регистрация)
MAX_EMAIL_VERIFICATION_ISSUANCES_PER_24H = 5


def hash_verification_token(raw: str) -> str:
    """SHA-256 hex для хранения в token_hash (сырой код в БД не храним)."""
    return hashlib.sha256(raw.strip().encode("utf-8")).hexdigest()


def build_email_verification_code(
    user_id: int,
    *,
    purpose: EmailVerificationPurpose = EmailVerificationPurpose.verify_email,
    resend_count: int = 0,
) -> tuple[str, EmailVerificationToken]:
    """
    6-значный цифровой код (с ведущими нулями), одноразовый, в БД только hash.
    Возвращает (код для письма один раз, ORM-строка).
    """
    n = secrets.randbelow(1_000_000)
    raw = f"{n:06d}"
    token_hash = hash_verification_token(raw)
    now = datetime.now(timezone.utc)
    row = EmailVerificationToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=now + timedelta(seconds=TOKEN_TTL_SECONDS),
        purpose=purpose,
        resend_count=resend_count,
    )
    return raw, row
