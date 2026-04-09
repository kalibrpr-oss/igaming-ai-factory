"""Значение mock в enum payment_provider (тестовый провайдер без кассы)."""

from __future__ import annotations

from alembic import op

revision = "0003_payment_provider_mock"
down_revision = "0002_payment_balance_layer"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # IF NOT EXISTS для ADD VALUE есть только в PG15+; ловим дубликат для повторного прогона.
    op.execute(
        """
        DO $$
        BEGIN
            ALTER TYPE payment_provider ADD VALUE 'mock';
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END $$;
        """
    )


def downgrade() -> None:
    # Удаление значения из ENUM в PostgreSQL без пересоздания типа не поддерживается.
    # При откате схемы вручную: удалить строки с provider=mock или пересоздать тип.
    pass
