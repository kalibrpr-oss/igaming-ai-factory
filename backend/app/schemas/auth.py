import re
from datetime import datetime
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, Field, field_validator

from app.services.auth.email_validation import ensure_deliverable_email

DeliverableEmail = Annotated[
    str,
    Field(min_length=3, max_length=320),
    AfterValidator(ensure_deliverable_email),
]


class RegisterRequest(BaseModel):
    email: DeliverableEmail
    username: str
    password: str = Field(min_length=8, max_length=128)
    referral_code: str | None = Field(
        default=None,
        max_length=32,
        description="Код пригласившего (из ?ref= или cookie на фронте).",
    )

    @field_validator("username", mode="before")
    @classmethod
    def register_username(cls, v: object) -> str:
        if not isinstance(v, str):
            raise ValueError("Ник должен быть текстом.")
        s = v.strip()
        if len(s) < 4:
            raise ValueError("Ник слишком короткий — нужно от 4 до 15 символов.")
        if len(s) > 15:
            raise ValueError("Ник слишком длинный — максимум 15 символов.")
        if not re.fullmatch(r"[a-zA-Z0-9]+", s):
            raise ValueError(
                "Ник: только английские буквы и цифры, без пробелов и других знаков."
            )
        return s


class LoginRequest(BaseModel):
    email: DeliverableEmail
    password: str = Field(min_length=1, max_length=128)


class EmailVerifyRequest(BaseModel):
    """6-значный код из письма (в БД хранится только hash)."""

    code: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
        description="Ровно 6 цифр",
    )


class ResendVerificationEmailRequest(BaseModel):
    """Повторная отправка кода для неподтверждённого аккаунта (без JWT — логин до verify запрещён)."""

    email: DeliverableEmail
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserPublic(BaseModel):
    id: int
    email: str
    username: str
    is_admin: bool
    is_email_verified: bool
    email_verified_at: datetime | None = None
    balance_cents: int = 0
    first_order_discount_active: bool = False

    model_config = {"from_attributes": True}


class RegisterResponse(UserPublic):
    """Ответ POST /auth/register: новый аккаунт создан или email уже ждёт подтверждения."""

    registration_status: Literal["created", "already_pending_verification"] = Field(
        description=(
            "created — новый пользователь создан, код выпущен; "
            "already_pending_verification — аккаунт уже существовал и ждёт подтверждения"
        ),
    )
    verification_delivery_status: Literal[
        "background_send_started", "sent", "cooldown"
    ] = Field(
        description=(
            "background_send_started — для новой регистрации письмо уходит в фоне; "
            "sent — для existing unverified новый код отправлен; "
            "cooldown — новый код пока нельзя отправить из-за cooldown"
        ),
    )
    resend_available_in_seconds: int | None = Field(
        default=None,
        ge=1,
        description="Через сколько секунд можно повторно запросить код, если сработал cooldown.",
    )


class VerifyEmailResponse(TokenResponse):
    user: UserPublic
