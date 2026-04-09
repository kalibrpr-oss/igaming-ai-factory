import logging
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.dependencies import get_current_user
from app.models.email_verification_token import EmailVerificationToken
from app.models.enums import EmailVerificationPurpose
from app.models.user import User
from app.schemas.auth import (
    EmailVerifyRequest,
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    ResendVerificationEmailRequest,
    TokenResponse,
    UserPublic,
    VerifyEmailResponse,
)
from app.services.auth.email_verification import (
    MAX_EMAIL_VERIFICATION_ISSUANCES_PER_24H,
    build_email_verification_code,
    hash_verification_token,
)
from app.services.auth.jwt_tokens import create_access_token
from app.services.auth.password import hash_password, verify_password
from app.services.mail.tasks import (
    send_verification_email_task,
    send_verification_email_task_safe,
)

router = APIRouter()
logger = logging.getLogger(__name__)

_VERIFY_WRONG = "Неверный код"
_VERIFY_EXPIRED = "Код истёк"
_VERIFY_USED = "Код уже использован"
_VERIFY_TOO_MANY = "Слишком много попыток подтверждения. Попробуйте позже."
_RESEND_TOO_SOON = "Слишком частый запрос нового кода. Повторите позже."
_LOGIN_FAIL = "Неверный email или пароль"
_VERIFY_RATE_WINDOW_SECONDS = 10 * 60
_VERIFY_RATE_MAX_ATTEMPTS = 10
_RESEND_MIN_INTERVAL_SECONDS = 60
_verify_attempts_by_ip: dict[str, deque[datetime]] = defaultdict(deque)


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _extract_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip() or "unknown"
    client_host = request.client.host if request.client else None
    return client_host or "unknown"


def _enforce_verify_attempt_limit(request: Request, now: datetime) -> None:
    client_ip = _extract_client_ip(request)
    attempts = _verify_attempts_by_ip[client_ip]
    window_start = now - timedelta(seconds=_VERIFY_RATE_WINDOW_SECONDS)
    while attempts and attempts[0] < window_start:
        attempts.popleft()
    if len(attempts) >= _VERIFY_RATE_MAX_ATTEMPTS:
        logger.warning(
            "verify blocked by rate limit: ip=%s attempts=%s window_sec=%s",
            client_ip,
            len(attempts),
            _VERIFY_RATE_WINDOW_SECONDS,
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=_VERIFY_TOO_MANY,
        )
    attempts.append(now)


def _register_response(
    user: User,
    registration_status: Literal["created", "already_pending_verification"],
    *,
    verification_delivery_status: Literal[
        "background_send_started", "sent", "cooldown"
    ],
    resend_available_in_seconds: int | None = None,
) -> RegisterResponse:
    return RegisterResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        is_admin=user.is_admin,
        is_email_verified=user.is_email_verified,
        email_verified_at=user.email_verified_at,
        balance_cents=user.balance_cents,
        registration_status=registration_status,
        verification_delivery_status=verification_delivery_status,
        resend_available_in_seconds=resend_available_in_seconds,
    )


async def _issue_verification_code(
    session: AsyncSession,
    user: User,
) -> tuple[str, int]:
    """Инвалидация активных кодов, лимит 24ч и выпуск нового 6-значного кода."""
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(hours=24)

    cnt = await session.scalar(
        select(func.count())
        .select_from(EmailVerificationToken)
        .where(
            EmailVerificationToken.user_id == user.id,
            EmailVerificationToken.purpose == EmailVerificationPurpose.verify_email,
            EmailVerificationToken.created_at >= window_start,
        )
    )
    if cnt is not None and cnt >= MAX_EMAIL_VERIFICATION_ISSUANCES_PER_24H:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Слишком много запросов. Попробуйте позже.",
        )

    await session.execute(
        update(EmailVerificationToken)
        .where(
            EmailVerificationToken.user_id == user.id,
            EmailVerificationToken.purpose == EmailVerificationPurpose.verify_email,
            EmailVerificationToken.consumed_at.is_(None),
        )
        .values(consumed_at=now)
    )

    max_rc = await session.scalar(
        select(func.coalesce(func.max(EmailVerificationToken.resend_count), -1)).where(
            EmailVerificationToken.user_id == user.id,
            EmailVerificationToken.purpose == EmailVerificationPurpose.verify_email,
        )
    )
    next_rc = int(max_rc) + 1

    raw_code, token_row = build_email_verification_code(
        user.id,
        purpose=EmailVerificationPurpose.verify_email,
        resend_count=next_rc,
    )
    session.add(token_row)
    await session.refresh(user)

    logger.info(
        "verification code issued: user_id=%s email=%s resend_count=%s",
        user.id,
        user.email,
        token_row.resend_count,
    )
    return raw_code, token_row.resend_count


async def _get_resend_cooldown_left_seconds(
    session: AsyncSession,
    user: User,
    *,
    now: datetime | None = None,
) -> int:
    now = now or datetime.now(timezone.utc)
    last_issued_at = await session.scalar(
        select(func.max(EmailVerificationToken.created_at)).where(
            EmailVerificationToken.user_id == user.id,
            EmailVerificationToken.purpose == EmailVerificationPurpose.verify_email,
        )
    )
    if last_issued_at is None:
        return 0
    last_issued_at_aware = (
        last_issued_at.replace(tzinfo=timezone.utc)
        if last_issued_at.tzinfo is None
        else last_issued_at
    )
    return max(
        0,
        _RESEND_MIN_INTERVAL_SECONDS - int((now - last_issued_at_aware).total_seconds()),
    )


async def _issue_verification_code_and_email(
    session: AsyncSession,
    user: User,
) -> None:
    """Resend: выпускаем код и подтверждаем факт отправки письма в том же запросе."""
    raw_code, resend_count = await _issue_verification_code(session, user)
    try:
        await send_verification_email_task(
            user.email,
            user.username,
            raw_code,
            resend_count,
        )
    except Exception as exc:
        logger.exception(
            "verification email send failed after code issued: user_id=%s email=%s",
            user.id,
            user.email,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Не удалось отправить письмо с кодом. Изменения не сохранены — "
                "повторите попытку позже."
            ),
        ) from exc


@router.post("/register", response_model=RegisterResponse)
async def register(
    body: RegisterRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
) -> RegisterResponse:
    email_norm = _normalize_email(body.email)

    existing = await session.execute(select(User).where(User.email == email_norm))
    user_existing = existing.scalar_one_or_none()

    if user_existing is not None:
        if user_existing.is_email_verified:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email уже зарегистрирован",
            )
        cooldown_left = await _get_resend_cooldown_left_seconds(session, user_existing)
        # Последний введённый пароль при повторной регистрации — источник истины для входа после verify.
        user_existing.hashed_password = hash_password(body.password)
        if cooldown_left > 0:
            logger.info(
                "register: existing unverified email on cooldown user_id=%s cooldown_left=%s",
                user_existing.id,
                cooldown_left,
            )
            return _register_response(
                user_existing,
                "already_pending_verification",
                verification_delivery_status="cooldown",
                resend_available_in_seconds=cooldown_left,
            )
        await _issue_verification_code_and_email(session, user_existing)
        logger.info(
            "register: existing unverified email redirected to verify flow user_id=%s",
            user_existing.id,
        )
        return _register_response(
            user_existing,
            "already_pending_verification",
            verification_delivery_status="sent",
        )

    exists_u = await session.execute(
        select(User).where(User.username == body.username.strip())
    )
    if exists_u.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Имя пользователя занято")

    user = User(
        email=email_norm,
        username=body.username.strip(),
        hashed_password=hash_password(body.password),
        is_email_verified=False,
        balance_cents=0,
    )
    session.add(user)
    try:
        await session.flush()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Конфликт данных") from None

    raw_code, resend_count = await _issue_verification_code(session, user)
    background_tasks.add_task(
        send_verification_email_task_safe,
        user.email,
        user.username,
        raw_code,
        resend_count,
    )
    return _register_response(
        user,
        "created",
        verification_delivery_status="background_send_started",
    )


@router.post("/verify-email", response_model=VerifyEmailResponse)
async def verify_email(
    body: EmailVerifyRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> VerifyEmailResponse:
    """Подтверждение email по 6-значному коду (без JWT)."""
    now = datetime.now(timezone.utc)
    _enforce_verify_attempt_limit(request, now)
    token_hash = hash_verification_token(body.code)
    result = await session.execute(
        select(EmailVerificationToken).where(
            EmailVerificationToken.token_hash == token_hash,
            EmailVerificationToken.purpose == EmailVerificationPurpose.verify_email,
        )
    )
    row = result.scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=400, detail=_VERIFY_WRONG)

    user = await session.get(User, row.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=400, detail=_VERIFY_WRONG)

    if row.consumed_at is not None:
        raise HTTPException(status_code=400, detail=_VERIFY_USED)
    expires_at = (
        row.expires_at.replace(tzinfo=timezone.utc)
        if row.expires_at.tzinfo is None
        else row.expires_at
    )
    if expires_at <= now:
        raise HTTPException(status_code=400, detail=_VERIFY_EXPIRED)
    if user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email уже подтверждён",
        )

    row.consumed_at = now
    user.is_email_verified = True
    user.email_verified_at = now

    token = create_access_token(str(user.id))
    await session.flush()
    return VerifyEmailResponse(
        access_token=token,
        user=UserPublic.model_validate(user),
    )


@router.post("/resend-verification-email", response_model=UserPublic)
async def resend_verification_email(
    body: ResendVerificationEmailRequest,
    session: AsyncSession = Depends(get_session),
) -> User:
    """
    Новый код для неподтверждённого email.
    JWT не используем: до verify логин запрещён, токен получить нельзя.
    Доступ по email + пароль (как при логине).
    """
    email_norm = _normalize_email(body.email)
    result = await session.execute(
        select(User).where(User.email == email_norm)
    )
    user = result.scalar_one_or_none()
    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail=_LOGIN_FAIL)
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Аккаунт отключён")
    if user.is_email_verified:
        raise HTTPException(
            status_code=400,
            detail="Email уже подтверждён",
        )
    cooldown_left = await _get_resend_cooldown_left_seconds(session, user)
    if cooldown_left > 0:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"{_RESEND_TOO_SOON} Осталось ~{cooldown_left} сек.",
        )

    logger.info(
        "resend verification email: запрос принят user_id=%s email=%s",
        user.id,
        user.email,
    )

    await _issue_verification_code_and_email(session, user)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    email_norm = _normalize_email(body.email)
    result = await session.execute(
        select(User).where(User.email == email_norm)
    )
    user = result.scalar_one_or_none()
    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Аккаунт отключён")
    if not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Сначала подтвердите email — введите код из письма на странице подтверждения.",
        )
    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserPublic)
async def me(user: User = Depends(get_current_user)) -> User:
    return user
