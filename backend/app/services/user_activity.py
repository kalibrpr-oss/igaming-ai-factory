"""Последний визит и грубая классификация устройства по User-Agent."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User

# Не дёргаем БД на каждый запрос: обновляем не чаще чем раз в N секунд.
_ACTIVITY_UPDATE_MIN_INTERVAL = timedelta(seconds=120)


def device_kind_from_user_agent(user_agent: str | None) -> str:
    """Ориентировочно: mobile / desktop / unknown (без претензии к точности)."""
    if not user_agent or not user_agent.strip():
        return "unknown"
    u = user_agent.lower()
    mobile_markers = (
        "mobile",
        "android",
        "iphone",
        "ipad",
        "ipod",
        "webos",
        "blackberry",
        "iemobile",
        "opera mini",
    )
    if any(m in u for m in mobile_markers):
        return "mobile"
    return "desktop"


def _normalize_ua(ua: str | None) -> str | None:
    if ua is None:
        return None
    s = ua.strip()
    if not s:
        return None
    return s[:512]


async def touch_user_activity_if_due(
    session: AsyncSession,
    user: User,
    user_agent: str | None,
) -> None:
    """Обновляет last_seen_at и last_user_agent с троттлингом."""
    now = datetime.now(timezone.utc)
    if user.last_seen_at is not None:
        # naive vs aware: нормализуем к UTC для сравнения
        prev = user.last_seen_at
        if prev.tzinfo is None:
            prev = prev.replace(tzinfo=timezone.utc)
        if now - prev < _ACTIVITY_UPDATE_MIN_INTERVAL:
            return
    user.last_seen_at = now
    user.last_user_agent = _normalize_ua(user_agent)
    await session.flush()
