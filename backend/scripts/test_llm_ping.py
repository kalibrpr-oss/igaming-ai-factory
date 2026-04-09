"""
Быстрая проверка ANTHROPIC_API_KEY и доступа к API (без полного заказа).

Запуск из папки backend:
  python scripts/test_llm_ping.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.services.llm.claude_client import call_claude_sync


def main() -> int:
    try:
        text = call_claude_sync(
            system="Отвечай максимально кратко.",
            user='Напиши одно слово: "ок" или "ошибка".',
            max_tokens=32,
        )
        print("Ответ модели:", text[:500])
        print("Проверка пройдена: ключ и сеть работают.")
        return 0
    except Exception as e:
        print("Ошибка:", e)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
