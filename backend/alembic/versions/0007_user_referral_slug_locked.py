"""referral_slug_locked — один раз сменить красивый slug.

Revision ID: 0007
Revises: 0006
Create Date: 2026-04-09
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0007_user_referral_slug_locked"
down_revision = "0006_order_moderation_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "referral_slug_locked",
            sa.Boolean(),
            server_default="false",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "referral_slug_locked")
