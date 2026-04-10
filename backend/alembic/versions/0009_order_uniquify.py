"""Заказ: режим generate/uniquify и исходный текст для уникализации.

Revision ID: 0009
Revises: 0008
Create Date: 2026-04-09
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0009_order_uniquify"
down_revision = "0008_user_last_seen_balance_note"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "orders",
        sa.Column(
            "order_kind",
            sa.String(length=16),
            nullable=False,
            server_default="generate",
        ),
    )
    op.add_column(
        "orders",
        sa.Column("source_text", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("orders", "source_text")
    op.drop_column("orders", "order_kind")
