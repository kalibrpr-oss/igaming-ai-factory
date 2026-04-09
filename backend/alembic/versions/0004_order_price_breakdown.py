"""Orders: добавляем price_base_cents и discount_cents."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0004_order_price_breakdown"
down_revision = "0003_payment_provider_mock"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("orders", sa.Column("price_base_cents", sa.Integer(), nullable=True))
    op.add_column("orders", sa.Column("discount_cents", sa.Integer(), nullable=True))

    op.execute(
        """
        UPDATE orders
        SET price_base_cents = price_cents,
            discount_cents = 0
        WHERE price_base_cents IS NULL OR discount_cents IS NULL
        """
    )

    op.alter_column("orders", "price_base_cents", nullable=False)
    op.alter_column("orders", "discount_cents", nullable=False)


def downgrade() -> None:
    op.drop_column("orders", "discount_cents")
    op.drop_column("orders", "price_base_cents")
