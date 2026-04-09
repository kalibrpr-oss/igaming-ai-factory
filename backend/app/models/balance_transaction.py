from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import BalanceReferenceType, BalanceTransactionType

if TYPE_CHECKING:
    from app.models.user import User


class BalanceTransaction(Base):
    """Журнал движений по балансу; источник истины вместе с user.balance_cents."""

    __tablename__ = "balance_transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    amount_cents: Mapped[int] = mapped_column(Integer)
    type: Mapped[BalanceTransactionType] = mapped_column(
        Enum(BalanceTransactionType, name="balance_transaction_type")
    )
    reference_type: Mapped[BalanceReferenceType] = mapped_column(
        Enum(BalanceReferenceType, name="balance_reference_type")
    )
    reference_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="balance_transactions")
