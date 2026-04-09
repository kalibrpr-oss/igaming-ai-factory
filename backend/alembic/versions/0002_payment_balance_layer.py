"""Платежи: kind, user_id, nullable order_id; журнал balance_transactions; частичный unique provider+external_id."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_payment_balance_layer"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()

    payment_kind = postgresql.ENUM(
        "order_payment", "wallet_topup", name="payment_kind", create_type=True
    )
    payment_kind.create(bind, checkfirst=True)

    balance_transaction_type = postgresql.ENUM(
        "topup",
        "order_debit",
        "referral_reward",
        "adjustment",
        name="balance_transaction_type",
        create_type=True,
    )
    balance_transaction_type.create(bind, checkfirst=True)

    balance_reference_type = postgresql.ENUM(
        "payment", "order", "manual", name="balance_reference_type", create_type=True
    )
    balance_reference_type.create(bind, checkfirst=True)

    op.add_column(
        "payments",
        sa.Column("user_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "payments",
        sa.Column(
            "kind",
            postgresql.ENUM(
                "order_payment",
                "wallet_topup",
                name="payment_kind",
                create_type=False,
            ),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE payments AS p
        SET user_id = o.user_id
        FROM orders AS o
        WHERE p.order_id = o.id
        """
    )
    op.execute(
        "UPDATE payments SET kind = 'order_payment' WHERE kind IS NULL"
    )

    op.alter_column("payments", "user_id", nullable=False)
    op.alter_column("payments", "kind", nullable=False)

    op.create_foreign_key(
        "fk_payments_user_id_users",
        "payments",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.alter_column("payments", "order_id", existing_type=sa.Integer(), nullable=True)

    op.create_index(
        "ix_payments_provider_external_id_unique",
        "payments",
        ["provider", "external_id"],
        unique=True,
        postgresql_where=sa.text("external_id IS NOT NULL"),
    )

    op.create_table(
        "balance_transactions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
        sa.Column(
            "type",
            postgresql.ENUM(
                "topup",
                "order_debit",
                "referral_reward",
                "adjustment",
                name="balance_transaction_type",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "reference_type",
            postgresql.ENUM(
                "payment",
                "order",
                "manual",
                name="balance_reference_type",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("reference_id", sa.Integer(), nullable=True),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key", name="uq_balance_transactions_idempotency_key"),
    )
    op.create_index(
        op.f("ix_balance_transactions_user_id"),
        "balance_transactions",
        ["user_id"],
    )
    op.create_index(
        op.f("ix_balance_transactions_reference_id"),
        "balance_transactions",
        ["reference_id"],
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_balance_transactions_reference_id"),
        table_name="balance_transactions",
    )
    op.drop_index(
        op.f("ix_balance_transactions_user_id"),
        table_name="balance_transactions",
    )
    op.drop_table("balance_transactions")

    op.drop_index(
        "ix_payments_provider_external_id_unique",
        table_name="payments",
    )

    op.execute("DELETE FROM payments WHERE order_id IS NULL")
    op.alter_column("payments", "order_id", existing_type=sa.Integer(), nullable=False)

    op.drop_constraint("fk_payments_user_id_users", "payments", type_="foreignkey")
    op.drop_column("payments", "kind")
    op.drop_column("payments", "user_id")

    op.execute("DROP TYPE IF EXISTS balance_reference_type")
    op.execute("DROP TYPE IF EXISTS balance_transaction_type")
    op.execute("DROP TYPE IF EXISTS payment_kind")
