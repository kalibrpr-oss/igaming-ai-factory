"""Общие фикстуры: без DNS deliverability в unit-тестах (стабильность CI/офлайн)."""

from __future__ import annotations

import pytest

from app.config import settings


@pytest.fixture(autouse=True)
def _email_deliverability_off_for_tests(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "email_check_deliverability", False)
