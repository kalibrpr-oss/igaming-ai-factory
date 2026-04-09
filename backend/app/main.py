import logging
from contextlib import asynccontextmanager

import asyncpg.exceptions as asyncpg_exc
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError, OperationalError

from app.api.v1.router import api_router
from app.config import settings
from app.db.session import engine, init_db

logger = logging.getLogger(__name__)


def _log_database_target() -> None:
    """Лог цели подключения без пароля (диагностика startup)."""
    u = make_url(settings.database_url)
    host = u.host or "?"
    port = u.port or 5432
    name = u.database or "?"
    user = u.username or "?"
    logger.info(
        "База данных (из DATABASE_URL): host=%s port=%s name=%s user=%s",
        host,
        port,
        name,
        user,
    )
    plen = len(u.password or "")
    if plen > 0 and plen < 8:
        logger.warning(
            "DATABASE_URL: пароль в строке — %s симв.; проверьте, что это реальный пароль "
            "пользователя %s в PostgreSQL, а не плейсхолдер (например ***).",
            plen,
            user,
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    _log_database_target()
    if settings.init_db_on_startup:
        await init_db()
    yield
    await engine.dispose()


app = FastAPI(
    title="iGaming AI-Factory API",
    version="0.2.0",
    lifespan=lifespan,
)

# JWT уходит в заголовке Authorization, не в cookie — credentials для CORS не нужны.
# Иначе allow_origins=["*"] + allow_credentials=True недопустима спецификацией: браузер
# режет ответ (типичная картина: фронт в Docker 172.x → API на 127.0.0.1).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.middleware("http")
async def _security_headers(request: Request, call_next):
    """Минимальные заголовки; защита от подделки данных только на сервере (валидация + JWT)."""
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    return response


_DB_UNAVAILABLE_MSG = (
    "Сервис базы данных временно недоступен. Повторите попытку позже."
)


@app.exception_handler(OperationalError)
async def _handle_operational_error(
    _request: Request, _exc: OperationalError
) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={"detail": _DB_UNAVAILABLE_MSG},
    )


@app.exception_handler(asyncpg_exc.ConnectionDoesNotExistError)
async def _handle_asyncpg_conn_gone(
    _request: Request, _exc: asyncpg_exc.ConnectionDoesNotExistError
) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={"detail": _DB_UNAVAILABLE_MSG},
    )


@app.exception_handler(DBAPIError)
async def _handle_dbapi_connection(
    _request: Request, exc: DBAPIError
) -> JSONResponse:
    """Обёртки asyncpg вокруг обрыва соединения — 503, остальное пробрасываем дальше."""
    orig = getattr(exc, "orig", None)
    if isinstance(
        orig,
        (
            asyncpg_exc.ConnectionDoesNotExistError,
            asyncpg_exc.InterfaceError,
        ),
    ):
        return JSONResponse(
            status_code=503,
            content={"detail": _DB_UNAVAILABLE_MSG},
        )
    raise exc


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
