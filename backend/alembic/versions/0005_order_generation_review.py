"""Orders: review_required status + generated_text."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0005_order_generation_review"
down_revision = "0004_order_price_breakdown"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            ALTER TYPE order_status ADD VALUE 'review_required';
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END $$;
        """
    )
    op.add_column("orders", sa.Column("generated_text", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("orders", "generated_text")
