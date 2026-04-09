"""
Alembic: синхронный движок psycopg v3 (postgresql+psycopg) по URL из settings.
Async URL с asyncpg подменяется на +psycopg — без psycopg2 (на Windows даёт UnicodeDecodeError
на русских сообщениях libpq при ошибках подключения).
"""
from __future__ import annotations

import os
import sys
from logging.config import fileConfig
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from sqlalchemy.engine import make_url

# До загрузки драйвера: часть сообщений libpq приходит до выставления client_encoding в connect_args
os.environ.setdefault("PGCLIENTENCODING", "UTF8")
os.environ.setdefault("PGOPTIONS", "-c lc_messages=C -c client_encoding=UTF8")

from alembic import context
from sqlalchemy import create_engine, pool

# Корень backend в PYTHONPATH (как при запуске uvicorn из backend/)
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.config import RESOLVED_DOTENV_PATH, settings  # noqa: E402
from app.db.base import Base  # noqa: E402

# Регистрация всех таблиц в metadata
import app.models  # noqa: E402, F401


def _alembic_log_db_target() -> None:
    """Диагностика: тот же settings, что и uvicorn; пароль не печатаем."""
    u = make_url(settings.database_url)
    raw_len = len(os.environ.get("DATABASE_URL", ""))
    print(
        "[alembic] dotenv_path="
        + repr(RESOLVED_DOTENV_PATH)
        + " raw_DATABASE_URL_len_os="
        + str(raw_len)
        + " db target: "
        f"host={u.host!r} port={u.port!r} database={u.database!r} user={u.username!r} "
        f"password_len={len(u.password or '')} driver={u.drivername!r}",
        file=sys.stderr,
        flush=True,
    )


config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_sync_database_url() -> str:
    url = settings.database_url
    if "+asyncpg" in url:
        url = url.replace("+asyncpg", "+psycopg", 1)
    elif "+psycopg2" in url:
        url = url.replace("+psycopg2", "+psycopg", 1)
    return _with_pg_client_encoding_query(url)


def _with_pg_client_encoding_query(url: str) -> str:
    """Offline-режим: client_encoding в query для libpq."""
    p = urlparse(url)
    qs = dict(parse_qsl(p.query, keep_blank_values=True))
    qs.setdefault("client_encoding", "utf8")
    return urlunparse(p._replace(query=urlencode(qs)))


def _alembic_connect_args() -> dict:
    """Сессия: UTF-8 + английские lc_messages (дублирует PGOPTIONS на уровне соединения)."""
    return {"options": "-c lc_messages=C -c client_encoding=UTF8"}


def run_migrations_offline() -> None:
    _alembic_log_db_target()
    url = get_sync_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    _alembic_log_db_target()
    connectable = create_engine(
        get_sync_database_url(),
        poolclass=pool.NullPool,
        connect_args=_alembic_connect_args(),
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
