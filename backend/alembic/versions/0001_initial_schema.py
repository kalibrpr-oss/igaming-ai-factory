"""Начальная схема: users, orders, payments, email_verification_tokens + enum-типы PG."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()

    order_status = postgresql.ENUM(
        "draft",
        "pending_payment",
        "paid",
        "generating",
        "completed",
        "failed",
        "cancelled",
        name="order_status",
        create_type=True,
    )
    order_status.create(bind, checkfirst=True)

    payment_provider = postgresql.ENUM(
        "yoomoney", "sbp", name="payment_provider", create_type=True
    )
    payment_provider.create(bind, checkfirst=True)

    payment_status = postgresql.ENUM(
        "pending", "succeeded", "failed", "refunded",
        name="payment_status",
        create_type=True,
    )
    payment_status.create(bind, checkfirst=True)

    email_verification_purpose = postgresql.ENUM(
        "verify_email", name="email_verification_purpose", create_type=True
    )
    email_verification_purpose.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_email_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("balance_cents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("referral_code", sa.String(length=32), nullable=True),
        sa.Column("referrer_user_id", sa.Integer(), nullable=True),
        sa.Column(
            "first_order_bonus_expires_at", sa.DateTime(timezone=True), nullable=True
        ),
        sa.Column(
            "first_order_bonus_consumed_at", sa.DateTime(timezone=True), nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["referrer_user_id"],
            ["users.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    op.create_index(
        op.f("ix_users_referral_code"), "users", ["referral_code"], unique=True
    )
    op.create_index(op.f("ix_users_referrer_user_id"), "users", ["referrer_user_id"])

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "draft",
                "pending_payment",
                "paid",
                "generating",
                "completed",
                "failed",
                "cancelled",
                name="order_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("brand_name", sa.String(length=256), nullable=False),
        sa.Column("task_notes", sa.Text(), nullable=True),
        sa.Column(
            "keywords",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "lsi_keywords",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "seo_config",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("target_word_count", sa.Integer(), nullable=False),
        sa.Column("price_cents", sa.Integer(), nullable=False),
        sa.Column("brand_voice_id", sa.String(length=64), nullable=False),
        sa.Column("generated_asset_uri", sa.String(length=512), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_orders_brand_voice_id"), "orders", ["brand_voice_id"])

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column(
            "provider",
            postgresql.ENUM(
                "yoomoney", "sbp", name="payment_provider", create_type=False
            ),
            nullable=False,
        ),
        sa.Column("external_id", sa.String(length=128), nullable=True),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False, server_default="RUB"),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending",
                "succeeded",
                "failed",
                "refunded",
                name="payment_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("raw_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_payments_external_id"), "payments", ["external_id"])

    op.create_table(
        "email_verification_tokens",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=128), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "purpose",
            postgresql.ENUM(
                "verify_email", name="email_verification_purpose", create_type=False
            ),
            nullable=False,
        ),
        sa.Column("resend_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_email_verification_tokens_user_id"),
        "email_verification_tokens",
        ["user_id"],
    )
    op.create_index(
        op.f("ix_email_verification_tokens_token_hash"),
        "email_verification_tokens",
        ["token_hash"],
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_email_verification_tokens_token_hash"),
        table_name="email_verification_tokens",
    )
    op.drop_index(
        op.f("ix_email_verification_tokens_user_id"),
        table_name="email_verification_tokens",
    )
    op.drop_table("email_verification_tokens")

    op.drop_index(op.f("ix_payments_external_id"), table_name="payments")
    op.drop_table("payments")

    op.drop_index(op.f("ix_orders_brand_voice_id"), table_name="orders")
    op.drop_table("orders")

    op.drop_index(op.f("ix_users_referrer_user_id"), table_name="users")
    op.drop_index(op.f("ix_users_referral_code"), table_name="users")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    op.execute("DROP TYPE IF EXISTS email_verification_purpose")
    op.execute("DROP TYPE IF EXISTS payment_status")
    op.execute("DROP TYPE IF EXISTS payment_provider")
    op.execute("DROP TYPE IF EXISTS order_status")
