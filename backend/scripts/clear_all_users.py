"""
Удаляет всех пользователей из БД (тестовые аккаунты).
Связанные строки (заказы, платежи, токены верификации и т.д.) уходят по ON DELETE CASCADE.

Запуск из папки backend:
  python scripts/clear_all_users.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Рабочая директория при двойном клике может быть не backend — подстрахуемся
_backend = Path(__file__).resolve().parent.parent
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from sqlalchemy import text  # noqa: E402

from app.db.session import engine  # noqa: E402


async def main() -> None:
    async with engine.begin() as conn:
        result = await conn.execute(text("DELETE FROM users"))
        n = result.rowcount
    print(f"Готово. Удалено пользователей: {n}")


if __name__ == "__main__":
    asyncio.run(main())
