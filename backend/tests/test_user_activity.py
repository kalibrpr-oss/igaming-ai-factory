import pytest

from app.services.user_activity import device_kind_from_user_agent


@pytest.mark.parametrize(
    ("ua", "expected"),
    [
        (None, "unknown"),
        ("", "unknown"),
        (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
            "mobile",
        ),
        (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "desktop",
        ),
        (
            "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36",
            "mobile",
        ),
    ],
)
def test_device_kind_from_user_agent(ua: str | None, expected: str) -> None:
    assert device_kind_from_user_agent(ua) == expected
