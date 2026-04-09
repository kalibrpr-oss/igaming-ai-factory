"""
Выдать пользователю права администратора по email.

Запуск только локально (читает DATABASE_URL из backend/.env).

Пример (из папки backend):
  python scripts/promote_admin.py azgeda79@yandex.ru
"""

from __future__ import annotations

import sys
from pathlib import Path

# Корень backend в PYTHONPATH
_BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from app.config import settings


def _sync_url(async_url: str) -> str:
    u = make_url(async_url)
    if "+asyncpg" in u.drivername:
        return str(u.set(drivername="postgresql+psycopg"))
    if u.drivername == "postgresql":
        return str(u.set(drivername="postgresql+psycopg"))
    return async_url


def main() -> int:
    if len(sys.argv) < 2:
        print(
            "Укажи почту. Пример:\n"
            "  python scripts/promote_admin.py твоя@почта.ru",
            file=sys.stderr,
        )
        return 2
    email = sys.argv[1].strip().lower()
    if not email or "@" not in email:
        print("Похоже, это не email.", file=sys.stderr)
        return 2

    url = _sync_url(settings.database_url)
    engine = create_engine(url)
    sql = text(
        'UPDATE users SET is_admin = true WHERE lower(btrim(email)) = lower(btrim(:email))'
    )
    try:
        with engine.begin() as conn:
            result = conn.execute(sql, {"email": email})
            n = result.rowcount
    except OSError as e:
        print(
            f"Не удалось подключиться к базе ({e}). "
            "Проверь, что PostgreSQL запущен и DATABASE_URL в backend/.env верный.",
            file=sys.stderr,
        )
        return 1
    except Exception as e:
        print(f"Ошибка БД: {e}", file=sys.stderr)
        return 1

    if n == 0:
        print(
            f'Пользователя с почтой «{email}» нет в базе. '
            f"Сначала зарегистрируйся на сайте, потом снова запусти эту команду."
        )
        return 1

    print(
        f"Готово: «{email}» теперь админ.\n"
        f"Выйди из аккаунта на сайте и зайди снова, затем открой страницу /admin "
        f"(например http://localhost:3000/admin)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
