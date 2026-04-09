"""Правила кастомного реферального slug."""

from app.services.referrals import validate_custom_referral_slug


def test_slug_allows_simple_code() -> None:
    assert validate_custom_referral_slug("mybrand") is None


def test_slug_rejects_reserved() -> None:
    assert validate_custom_referral_slug("admin") is not None


def test_slug_rejects_invalid_chars() -> None:
    assert validate_custom_referral_slug("привет") is not None


def test_slug_rejects_trailing_hyphen() -> None:
    assert validate_custom_referral_slug("abc-") is not None
