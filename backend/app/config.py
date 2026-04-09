import os
import sys
from pathlib import Path

from dotenv import dotenv_values, load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Только этот файл .env (не родительский репозиторий, не .env.example).
_ABSOLUTE_ENV = Path(r"C:\Users\user\Desktop\iGaming Project\backend\.env")
_FALLBACK_ENV = Path(__file__).resolve().parent.parent / ".env"
_ENV_FILE = _ABSOLUTE_ENV if _ABSOLUTE_ENV.is_file() else _FALLBACK_ENV
# Для alembic / ручной проверки: какой файл .env реально использован
RESOLVED_DOTENV_PATH = str(_ENV_FILE.resolve())

# Снимок до загрузки (источник «старого» значения — обычно Windows User/System env)
_database_url_before = os.environ.get("DATABASE_URL")
load_dotenv(_ENV_FILE, override=True)

# Парсинг файла напрямую — обход сюрпризов load_dotenv + единая правда для DATABASE_URL
_file_map = dotenv_values(_ENV_FILE)
_raw_database_url_from_file = (_file_map.get("DATABASE_URL") or "").strip().strip('"').strip("'")
if _raw_database_url_from_file:
    os.environ["DATABASE_URL"] = _raw_database_url_from_file


def _password_len_from_url(url: str) -> int:
    if not url:
        return 0
    try:
        from sqlalchemy.engine import make_url

        u = make_url(url)
        return len(u.password or "")
    except Exception:
        return -1


def _log_env_resolution() -> None:
    """Один раз при импорте: куда смотрим и что получилось (пароль не печатаем)."""
    after = os.environ.get("DATABASE_URL", "")
    src = (
        "file(dotenv_values)"
        if _raw_database_url_from_file
        else ("os.environ (unchanged)" if after == _database_url_before else "load_dotenv only")
    )
    print(
        "[conveer-config] "
        f"env_path={_ENV_FILE.resolve()} exists={_ENV_FILE.is_file()} "
        f"used_absolute_primary={_ABSOLUTE_ENV.is_file()} "
        f"raw_DATABASE_URL_len_file={len(_raw_database_url_from_file)} "
        f"os_DATABASE_URL_len_before={len(_database_url_before or '')} "
        f"os_DATABASE_URL_len_after={len(after)} "
        f"password_len_parsed={_password_len_from_url(after)} "
        f"source_hint={src!r}",
        file=sys.stderr,
        flush=True,
    )


_log_env_resolution()


class Settings(BaseSettings):
    # Только os.environ после явной загрузки backend/.env — без второго чтения другого пути.
    model_config = SettingsConfigDict(extra="ignore")

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/igaming_factory",
        description="Async SQLAlchemy URL (postgresql+asyncpg://...). Читается из DATABASE_URL.",
    )
    init_db_on_startup: bool = Field(
        default=False,
        description="Вызывать init_db() (metadata.create_all) в lifespan",
    )
    redis_url: str = "redis://127.0.0.1:6379/0"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    jwt_secret: str = "dev-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7

    price_per_100_words_cents: int = 2900

    mail_transport: str = Field(default="logging", description="logging | smtp")
    mail_from_address: str = Field(default="noreply@localhost")
    mail_from_name: str = Field(default="iGaming AI-Factory")
    mail_from_email: str = Field(default="", description="From email для SMTP")

    smtp_host: str = Field(default="")
    smtp_port: int = Field(default=587)
    smtp_user: str = Field(default="")
    smtp_password: str = Field(default="")

    enable_internal_wallet_test_flow: bool = Field(
        default=False,
        description="Включает POST /api/v1/internal/wallet-test/* (только с admin JWT)",
    )

    email_check_deliverability: bool = Field(
        default=True,
        description=(
            "DNS-проверка домена email (MX/A) при регистрации, входе и resend. "
            "Для тестов без сети: EMAIL_CHECK_DELIVERABILITY=false"
        ),
    )


settings = Settings()
