"""Orders: поля ручной модерации (moderated_at, moderated_by_user_id, moderation_notes)."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0006_order_moderation_fields"
down_revision = "0005_order_generation_review"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "orders",
        sa.Column("moderated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "orders",
        sa.Column("moderated_by_user_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "orders",
        sa.Column("moderation_notes", sa.Text(), nullable=True),
    )
    op.create_foreign_key(
        "fk_orders_moderated_by_user_id_users",
        "orders",
        "users",
        ["moderated_by_user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_orders_moderated_by_user_id",
        "orders",
        ["moderated_by_user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_orders_moderated_by_user_id", table_name="orders")
    op.drop_constraint(
        "fk_orders_moderated_by_user_id_users",
        "orders",
        type_="foreignkey",
    )
    op.drop_column("orders", "moderation_notes")
    op.drop_column("orders", "moderated_by_user_id")
    op.drop_column("orders", "moderated_at")
