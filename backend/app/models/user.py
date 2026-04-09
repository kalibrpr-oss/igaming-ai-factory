from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.balance_transaction import BalanceTransaction
    from app.models.email_verification_token import EmailVerificationToken
    from app.models.order import Order
    from app.models.payment import Payment


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    email_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    balance_cents: Mapped[int] = mapped_column(Integer, default=0)

    referral_code: Mapped[str | None] = mapped_column(
        String(32), unique=True, nullable=True, index=True
    )
    # Один раз сменить slug в ЛК; после True — кастом зафиксирован.
    referral_slug_locked: Mapped[bool] = mapped_column(default=False)
    referrer_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    first_order_bonus_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    first_order_bonus_consumed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)

    orders: Mapped[list["Order"]] = relationship(
        "Order",
        foreign_keys="Order.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    moderated_orders: Mapped[list["Order"]] = relationship(
        "Order",
        foreign_keys="Order.moderated_by_user_id",
        back_populates="moderator",
    )
    payments: Mapped[list["Payment"]] = relationship(
        "Payment",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    balance_transactions: Mapped[list["BalanceTransaction"]] = relationship(
        "BalanceTransaction",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    email_verification_tokens: Mapped[list["EmailVerificationToken"]] = relationship(
        "EmailVerificationToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    referrer: Mapped["User | None"] = relationship(
        "User",
        remote_side="User.id",
        foreign_keys=[referrer_user_id],
        back_populates="referrals",
    )
    referrals: Mapped[list["User"]] = relationship(
        "User",
        foreign_keys=[referrer_user_id],
        back_populates="referrer",
    )
