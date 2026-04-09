"""Простой текст писем без шаблонизатора (позже можно заменить на HTML + Jinja)."""


def build_verification_email_text(
    *,
    username: str,
    raw_token: str,
    resend_count: int,
) -> str:
    """Короткое plaintext-письмо: 6-значный код, 15 минут TTL."""
    _ = resend_count  # зарезервировано (например «повторная отправка №N»)
    greeting = f"Здравствуйте, {username}." if username else "Здравствуйте."
    return (
        f"{greeting}\n\n"
        "Код подтверждения email (6 цифр):\n\n"
        f"{raw_token}\n\n"
        "Код одноразовый, действует 15 минут.\n"
        "Если вы не регистрировались, проигнорируйте это письмо.\n"
    )
