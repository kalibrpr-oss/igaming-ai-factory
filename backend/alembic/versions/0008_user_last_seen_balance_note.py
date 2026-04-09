"""last_seen + user_agent; note у проводок для админ-выдачи.

Revision ID: 0008
Revises: 0007
Create Date: 2026-04-09
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0008_user_last_seen_balance_note"
down_revision = "0007_user_referral_slug_locked"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("last_user_agent", sa.String(length=512), nullable=True),
    )
    op.add_column(
        "balance_transactions",
        sa.Column("note", sa.String(length=512), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("balance_transactions", "note")
    op.drop_column("users", "last_user_agent")
    op.drop_column("users", "last_seen_at")
