import asyncio
import contextlib
import logging
from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.db.base import Base

logger = logging.getLogger(__name__)

# Повтор только при ошибке checkout/ping до yield — не дублирует бизнес-логику эндпоинта.
_SESSION_CONNECT_RETRIES = 3
_SESSION_RETRY_BASE_DELAY_SEC = 0.15

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_timeout=30,
    connect_args={
        # asyncpg: локально без SSL; таймаут операций на стороне драйвера (сек.)
        "ssl": False,
        "command_timeout": 120,
    },
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def _acquire_session_after_ping_with_retry() -> AsyncSession:
    """Открывает сессию и проверяет соединение; при сбое — несколько попыток (только до выдачи session)."""
    last: BaseException | None = None
    for attempt in range(_SESSION_CONNECT_RETRIES):
        session: AsyncSession | None = None
        try:
            session = AsyncSessionLocal()
            await session.__aenter__()
            await session.execute(text("SELECT 1"))
            return session
        except (OperationalError, DBAPIError, OSError, ConnectionError) as exc:
            last = exc
            if session is not None:
                with contextlib.suppress(BaseException):
                    await session.__aexit__(type(exc), exc, exc.__traceback__)
            if attempt < _SESSION_CONNECT_RETRIES - 1:
                delay = _SESSION_RETRY_BASE_DELAY_SEC * (2**attempt)
                logger.warning(
                    "Ошибка подключения к БД (попытка %s/%s), повтор через %.2fs: %s",
                    attempt + 1,
                    _SESSION_CONNECT_RETRIES,
                    delay,
                    exc,
                )
                await asyncio.sleep(delay)
                continue
            raise last


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session = await _acquire_session_after_ping_with_retry()
    try:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
    finally:
        with contextlib.suppress(BaseException):
            await session.close()


async def init_db() -> None:
    """
    Локально/тесты: быстро создать таблицы из metadata без миграций.

    Продакшен и долговременная схема: только `alembic upgrade head`.
    Не смешивайте на одной БД и create_all, и alembic без `alembic stamp` —
    при уже существующих таблицах из create_all выполните `alembic stamp head`.
    """
    import app.models  # noqa: F401 — регистрация метаданных таблиц

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
