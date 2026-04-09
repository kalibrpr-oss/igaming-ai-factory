from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.v1 import auth
from app.models.email_verification_token import EmailVerificationToken
from app.models.enums import EmailVerificationPurpose
from app.models.user import User
from app.services.mail import tasks as mail_tasks
from app.config import settings
from app.services.auth.email_verification import build_email_verification_code
from app.services.auth.password import hash_password, verify_password


def _run(coro):
    return asyncio.run(coro)


@pytest.fixture
async def session_maker() -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(User.__table__.create)
        await conn.run_sync(EmailVerificationToken.__table__.create)
    try:
        yield maker
    finally:
        await engine.dispose()


@pytest.fixture
def client(session_maker: async_sessionmaker[AsyncSession]) -> TestClient:
    app = FastAPI()
    app.include_router(auth.router, prefix="/api/v1/auth")

    async def override_get_session():
        async with session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[auth.get_session] = override_get_session
    auth._verify_attempts_by_ip.clear()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    auth._verify_attempts_by_ip.clear()


async def _create_user(
    session_maker: async_sessionmaker[AsyncSession],
    *,
    email: str,
    username: str,
    password: str,
    is_email_verified: bool = False,
    referral_code: str | None = None,
) -> User:
    async with session_maker() as session:
        user = User(
            email=email,
            username=username,
            hashed_password=hash_password(password),
            is_email_verified=is_email_verified,
            balance_cents=0,
            referral_code=referral_code,
            referral_slug_locked=False,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def _create_token(
    session_maker: async_sessionmaker[AsyncSession],
    *,
    user_id: int,
    raw_code: str | None = None,
    expires_at: datetime | None = None,
    consumed_at: datetime | None = None,
    created_at: datetime | None = None,
    resend_count: int = 0,
) -> str:
    raw, row = build_email_verification_code(
        user_id,
        purpose=EmailVerificationPurpose.verify_email,
        resend_count=resend_count,
    )
    if raw_code is not None:
        raw = raw_code
        _, row = build_email_verification_code(
            user_id,
            purpose=EmailVerificationPurpose.verify_email,
            resend_count=resend_count,
        )
        row.token_hash = auth.hash_verification_token(raw_code)
    if expires_at is not None:
        row.expires_at = expires_at
    row.consumed_at = consumed_at
    if created_at is not None:
        row.created_at = created_at

    async with session_maker() as session:
        session.add(row)
        await session.commit()
    return raw


async def _count_users(session_maker: async_sessionmaker[AsyncSession], email: str) -> int:
    async with session_maker() as session:
        return int(
            await session.scalar(select(func.count()).select_from(User).where(User.email == email))
            or 0
        )


async def _active_tokens_count(
    session_maker: async_sessionmaker[AsyncSession], user_id: int
) -> int:
    async with session_maker() as session:
        return int(
            await session.scalar(
                select(func.count())
                .select_from(EmailVerificationToken)
                .where(
                    EmailVerificationToken.user_id == user_id,
                    EmailVerificationToken.purpose == EmailVerificationPurpose.verify_email,
                    EmailVerificationToken.consumed_at.is_(None),
                )
            )
            or 0
        )


def test_register_rejects_typo_domain_when_deliverability_enabled(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Опечатка .ry вместо .ru — DNS не находит домен, письмо не должно уходить."""
    monkeypatch.setattr(settings, "email_check_deliverability", True)
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@mail.ry",
            "username": "typouser",
            "password": "Password123!",
        },
    )
    assert resp.status_code == 422


def test_register_rejects_invalid_username(client: TestClient) -> None:
    short = client.post(
        "/api/v1/auth/register",
        json={
            "email": "nick@example.com",
            "username": "ab",
            "password": "Password123!",
        },
    )
    assert short.status_code == 422
    badchars = client.post(
        "/api/v1/auth/register",
        json={
            "email": "nick2@example.com",
            "username": "bad_name",
            "password": "Password123!",
        },
    )
    assert badchars.status_code == 422


def test_register_new_email_success_creates_user_and_active_token(
    client: TestClient, session_maker: async_sessionmaker[AsyncSession], monkeypatch: pytest.MonkeyPatch
) -> None:
    async def _ok_send(*_args, **_kwargs) -> None:
        return None

    monkeypatch.setattr(mail_tasks, "send_verification_email_task", _ok_send)

    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "new@example.com", "username": "newuser12", "password": "Password123!"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["registration_status"] == "created"
    assert body["verification_delivery_status"] == "background_send_started"

    user_count = _run(_count_users(session_maker, "new@example.com"))
    assert user_count == 1
    user = _run(_fetch_user_by_email(session_maker, "new@example.com"))
    assert user is not None
    active_tokens = _run(_active_tokens_count(session_maker, user.id))
    assert active_tokens == 1


async def _fetch_user_by_email(
    session_maker: async_sessionmaker[AsyncSession], email: str
) -> User | None:
    async with session_maker() as session:
        result = await session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()


def test_register_new_email_background_delivery_fail_keeps_consistent_state(
    client: TestClient, session_maker: async_sessionmaker[AsyncSession], monkeypatch: pytest.MonkeyPatch
) -> None:
    async def _fail_send(*_args, **_kwargs) -> None:
        raise RuntimeError("smtp down")

    monkeypatch.setattr(mail_tasks, "send_verification_email_task", _fail_send)

    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "rollback@example.com", "username": "rollbackuser", "password": "Password123!"},
    )
    assert resp.status_code == 200
    assert resp.json()["registration_status"] == "created"
    assert resp.json()["verification_delivery_status"] == "background_send_started"

    user_count = _run(_count_users(session_maker, "rollback@example.com"))
    assert user_count == 1
    user = _run(_fetch_user_by_email(session_maker, "rollback@example.com"))
    assert user is not None
    assert _run(_active_tokens_count(session_maker, user.id)) == 1


def test_register_existing_unverified_sends_new_code_and_updates_password(
    client: TestClient, session_maker: async_sessionmaker[AsyncSession], monkeypatch: pytest.MonkeyPatch
) -> None:
    async def _ok_send(*_args, **_kwargs) -> None:
        return None

    monkeypatch.setattr(auth, "send_verification_email_task", _ok_send)

    user = _run(
        _create_user(
            session_maker,
            email="pending@example.com",
            username="pending_name",
            password="OldPassword123!",
        )
    )
    old_token_raw = _run(
        _create_token(
            session_maker,
            user_id=user.id,
            resend_count=0,
            created_at=datetime.now(timezone.utc) - timedelta(minutes=2),
        )
    )

    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "pending@example.com", "username": "pendingnew", "password": "NewPassword123!"},
    )
    assert resp.status_code == 200
    assert resp.json()["registration_status"] == "already_pending_verification"
    assert resp.json()["verification_delivery_status"] == "sent"

    user_after = _run(_fetch_user_by_email(session_maker, "pending@example.com"))
    assert user_after is not None
    assert user_after.id == user.id
    assert user_after.username == "pending_name"
    assert verify_password("NewPassword123!", user_after.hashed_password)
    assert not verify_password("OldPassword123!", user_after.hashed_password)

    active_tokens = _run(_active_tokens_count(session_maker, user.id))
    assert active_tokens == 1
    verify_old = client.post("/api/v1/auth/verify-email", json={"code": old_token_raw})
    assert verify_old.status_code == 400
    assert verify_old.json()["detail"] == "Код уже использован"


def test_register_existing_unverified_respects_cooldown_and_keeps_current_code(
    client: TestClient, session_maker: async_sessionmaker[AsyncSession], monkeypatch: pytest.MonkeyPatch
) -> None:
    async def _ok_send(*_args, **_kwargs) -> None:
        return None

    monkeypatch.setattr(auth, "send_verification_email_task", _ok_send)

    user = _run(
        _create_user(
            session_maker,
            email="pending-cooldown@example.com",
            username="pending_cooldown",
            password="Password123!",
        )
    )
    old_token_raw = _run(_create_token(session_maker, user_id=user.id, resend_count=0))

    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": "pending-cooldown@example.com",
            "username": "anothername",
            "password": "AnotherPassword123!",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["registration_status"] == "already_pending_verification"
    assert resp.json()["verification_delivery_status"] == "cooldown"
    assert isinstance(resp.json()["resend_available_in_seconds"], int)

    user_after = _run(_fetch_user_by_email(session_maker, "pending-cooldown@example.com"))
    assert user_after is not None
    assert user_after.id == user.id
    assert user_after.username == "pending_cooldown"
    assert verify_password("AnotherPassword123!", user_after.hashed_password)

    active_tokens = _run(_active_tokens_count(session_maker, user.id))
    assert active_tokens == 1
    verify_old = client.post("/api/v1/auth/verify-email", json={"code": old_token_raw})
    assert verify_old.status_code == 200
    assert isinstance(verify_old.json()["access_token"], str)


def test_register_existing_unverified_is_found_by_normalized_email(
    client: TestClient,
    session_maker: async_sessionmaker[AsyncSession],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _ok_send(*_args, **_kwargs) -> None:
        return None

    monkeypatch.setattr(auth, "send_verification_email_task", _ok_send)

    user = _run(
        _create_user(
            session_maker,
            email="pending-normalized@example.com",
            username="pending_normalized",
            password="Password123!",
        )
    )

    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": "  PENDING-NORMALIZED@EXAMPLE.COM  ",
            "username": "anothername",
            "password": "AnotherPassword123!",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["registration_status"] == "already_pending_verification"
    assert resp.json()["verification_delivery_status"] == "sent"

    user_after = _run(_fetch_user_by_email(session_maker, "pending-normalized@example.com"))
    assert user_after is not None
    assert user_after.id == user.id
    assert user_after.username == "pending_normalized"
    assert verify_password("AnotherPassword123!", user_after.hashed_password)


def test_register_existing_verified_email_returns_conflict(
    client: TestClient, session_maker: async_sessionmaker[AsyncSession]
) -> None:
    user = _run(
        _create_user(
            session_maker,
            email="verified@example.com",
            username="verified_user",
            password="Password123!",
            is_email_verified=True,
        )
    )

    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": "verified@example.com",
            "username": "badnewname",
            "password": "BrandNewPassword123!",
        },
    )
    assert resp.status_code == 409
    assert resp.json()["detail"] == "Email уже зарегистрирован"


def test_register_existing_verified_is_rejected_after_email_normalization(
    client: TestClient, session_maker: async_sessionmaker[AsyncSession]
) -> None:
    _run(
        _create_user(
            session_maker,
            email="verified-normalized@example.com",
            username="verified_normalized",
            password="Password123!",
            is_email_verified=True,
        )
    )

    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": "  VERIFIED-NORMALIZED@EXAMPLE.COM  ",
            "username": "freshname",
            "password": "FreshPassword123!",
        },
    )
    assert resp.status_code == 409
    assert resp.json()["detail"] == "Email уже зарегистрирован"


def test_verify_wrong_expired_used_and_success(
    client: TestClient, session_maker: async_sessionmaker[AsyncSession], monkeypatch: pytest.MonkeyPatch
) -> None:
    async def _ok_send(*_args, **_kwargs) -> None:
        return None

    monkeypatch.setattr(mail_tasks, "send_verification_email_task", _ok_send)

    user = _run(
        _create_user(
            session_maker,
            email="verify@example.com",
            username="verify_user",
            password="Password123!",
        )
    )
    raw_ok = _run(
        _create_token(session_maker, user_id=user.id, resend_count=0)
    )
    raw_expired = _run(
        _create_token(
            session_maker,
            user_id=user.id,
            expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
            resend_count=1,
        )
    )

    wrong = client.post("/api/v1/auth/verify-email", json={"code": "000000"})
    assert wrong.status_code == 400
    assert wrong.json()["detail"] == "Неверный код"

    expired = client.post("/api/v1/auth/verify-email", json={"code": raw_expired})
    assert expired.status_code == 400
    assert expired.json()["detail"] == "Код истёк"

    ok = client.post("/api/v1/auth/verify-email", json={"code": raw_ok})
    assert ok.status_code == 200
    assert isinstance(ok.json()["access_token"], str)
    assert ok.json()["user"]["email"] == "verify@example.com"
    used = client.post("/api/v1/auth/verify-email", json={"code": raw_ok})
    assert used.status_code == 400
    assert used.json()["detail"] == "Код уже использован"


def test_verify_rate_limit_blocks_bruteforce(client: TestClient) -> None:
    for _ in range(10):
        resp = client.post("/api/v1/auth/verify-email", json={"code": "123456"})
        assert resp.status_code == 400
    blocked = client.post("/api/v1/auth/verify-email", json={"code": "123456"})
    assert blocked.status_code == 429
    assert "Слишком много попыток" in blocked.json()["detail"]


def test_resend_success_cooldown_and_mail_fail_rollback(
    client: TestClient, session_maker: async_sessionmaker[AsyncSession], monkeypatch: pytest.MonkeyPatch
) -> None:
    async def _ok_send(*_args, **_kwargs) -> None:
        return None

    monkeypatch.setattr(auth, "send_verification_email_task", _ok_send)

    user = _run(
        _create_user(
            session_maker,
            email="resend@example.com",
            username="resend_user",
            password="Password123!",
        )
    )
    old_raw = _run(
        _create_token(
            session_maker,
            user_id=user.id,
            created_at=datetime.now(timezone.utc) - timedelta(minutes=2),
            resend_count=0,
        )
    )

    success = client.post(
        "/api/v1/auth/resend-verification-email",
        json={"email": "resend@example.com", "password": "Password123!"},
    )
    assert success.status_code == 200
    active_tokens = _run(_active_tokens_count(session_maker, user.id))
    assert active_tokens == 1
    old_check = client.post("/api/v1/auth/verify-email", json={"code": old_raw})
    assert old_check.status_code == 400
    assert old_check.json()["detail"] == "Код уже использован"

    too_soon = client.post(
        "/api/v1/auth/resend-verification-email",
        json={"email": "resend@example.com", "password": "Password123!"},
    )
    assert too_soon.status_code == 429
    assert "Слишком частый запрос нового кода" in too_soon.json()["detail"]

    async def _fail_send(*_args, **_kwargs) -> None:
        raise RuntimeError("smtp down")

    monkeypatch.setattr(auth, "send_verification_email_task", _fail_send)
    stale_created = datetime.now(timezone.utc) - timedelta(minutes=2)
    _run(_set_latest_token_created_at(session_maker, user.id, stale_created))
    fail = client.post(
        "/api/v1/auth/resend-verification-email",
        json={"email": "resend@example.com", "password": "Password123!"},
    )
    assert fail.status_code == 503
    active_after_fail = _run(_active_tokens_count(session_maker, user.id))
    assert active_after_fail == 1


async def _set_latest_token_created_at(
    session_maker: async_sessionmaker[AsyncSession], user_id: int, created_at: datetime
) -> None:
    async with session_maker() as session:
        result = await session.execute(
            select(EmailVerificationToken)
            .where(
                EmailVerificationToken.user_id == user_id,
                EmailVerificationToken.purpose == EmailVerificationPurpose.verify_email,
            )
            .order_by(EmailVerificationToken.id.desc())
            .limit(1)
        )
        token = result.scalar_one()
        token.created_at = created_at
        await session.commit()


def test_register_with_referral_code_sets_referrer(
    client: TestClient,
    session_maker: async_sessionmaker[AsyncSession],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _ok_send(*_args, **_kwargs) -> None:
        return None

    monkeypatch.setattr(mail_tasks, "send_verification_email_task", _ok_send)

    inv = _run(
        _create_user(
            session_maker,
            email="inviter@example.com",
            username="inviter42",
            password="Password123!",
            is_email_verified=True,
            referral_code="myinvite01",
        )
    )

    resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": "refchild@example.com",
            "username": "refchild99",
            "password": "Password123!",
            "referral_code": "myinvite01",
        },
    )
    assert resp.status_code == 200
    child = _run(_fetch_user_by_email(session_maker, "refchild@example.com"))
    assert child is not None
    assert child.referrer_user_id == inv.id
    assert child.referral_code is not None
    assert len(child.referral_code) >= 8
