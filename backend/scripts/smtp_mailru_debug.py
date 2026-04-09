#!/usr/bin/env python3
"""
Изолированная диагностика SMTP Mail.ru. Не трогает FastAPI и не импортирует app.*.

Запуск из каталога backend:
  python scripts/smtp_mailru_debug.py получатель@example.com

Переменные из backend/.env: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, MAIL_FROM_EMAIL
(опционально MAIL_FROM_NAME)
"""
from __future__ import annotations

import os
import smtplib
import sys
import traceback
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path

from dotenv import load_dotenv

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_ENV_PATH = _BACKEND_ROOT / ".env"


def _step(name: str, ok: bool, detail: str = "") -> None:
    status = "OK" if ok else "FAILED"
    line = f"[smtp-debug] {name}: {status}"
    if detail:
        line += f" — {detail}"
    print(line, flush=True)


def main() -> int:
    to_addr = sys.argv[1] if len(sys.argv) > 1 else None
    if not to_addr:
        print(
            "Usage: python scripts/smtp_mailru_debug.py <recipient@email>",
            file=sys.stderr,
        )
        return 2

    print(f"[smtp-debug] env file: {_ENV_PATH.resolve()}", flush=True)
    if not _ENV_PATH.is_file():
        _step("env file exists", False, str(_ENV_PATH))
        return 1
    _step("env file exists", True)

    load_dotenv(_ENV_PATH, override=True)
    _step("dotenv load_dotenv", True)

    host = (os.getenv("SMTP_HOST") or "").strip()
    port_s = (os.getenv("SMTP_PORT") or "587").strip()
    user = (os.getenv("SMTP_USER") or "").strip()
    password = os.getenv("SMTP_PASSWORD") or ""
    mail_from = (os.getenv("MAIL_FROM_EMAIL") or os.getenv("MAIL_FROM_ADDRESS") or "").strip()
    mail_name = (os.getenv("MAIL_FROM_NAME") or "").strip()

    try:
        port = int(port_s)
    except ValueError:
        port = 587
        _step("SMTP_PORT parse", False, f"bad value {port_s!r}, using 587")

    print(
        f"[smtp-debug] host={host!r} port={port} user={user!r} "
        f"from={mail_from!r} password_len={len(password)}",
        flush=True,
    )

    if not host or not user or not password:
        _step("required vars", False, "need SMTP_HOST, SMTP_USER, SMTP_PASSWORD")
        return 1
    if not mail_from:
        _step("MAIL_FROM_EMAIL", False, "empty — Mail.ru обычно требует From = тот же ящик, что SMTP_USER")
        return 1

    smtp: smtplib.SMTP | None = None
    try:
        try:
            smtp = smtplib.SMTP(host, port, timeout=30)
            _step("connect", True)
        except OSError as e:
            _step("connect", False, repr(e))
            return 1

        try:
            smtp.ehlo()
            _step("EHLO", True)
        except smtplib.SMTPException as e:
            _step("EHLO", False, repr(e))
            return 1

        try:
            smtp.starttls()
            smtp.ehlo()
            _step("STARTTLS", True)
        except smtplib.SMTPException as e:
            _step("STARTTLS", False, repr(e))
            return 1

        try:
            smtp.login(user, password)
            _step("login", True)
        except smtplib.SMTPAuthenticationError as e:
            code = getattr(e, "smtp_code", None)
            err = getattr(e, "smtp_error", b"")
            try:
                err_txt = err.decode("utf-8", errors="replace")
            except Exception:
                err_txt = repr(err)
            _step("login", False, f"code={code} smtp_error={err_txt!r} full={e!r}")
            print("[smtp-debug] SMTP полная ошибка (repr):", repr(e), flush=True)
            print(
                "[smtp-debug] Подсказка Mail.ru 535: нужен пароль приложения "
                "(не пароль входа в почту). Создать в настройках VK ID / Mail.ru.",
                flush=True,
            )
            return 1
        except smtplib.SMTPException as e:
            _step("login", False, repr(e))
            print("[smtp-debug] SMTP полная ошибка (repr):", repr(e), flush=True)
            return 1

        msg = EmailMessage()
        msg["Subject"] = "Conveer SMTP debug test"
        msg["From"] = formataddr((mail_name, mail_from)) if mail_name else mail_from
        msg["To"] = to_addr
        msg.set_content(
            "Тестовое письмо из scripts/smtp_mailru_debug.py\n"
            "Если видишь это — SMTP login + send прошли."
        )

        try:
            smtp.send_message(msg)
            _step("send_message", True, f"to={to_addr!r}")
        except smtplib.SMTPException as e:
            _step("send_message", False, repr(e))
            print("[smtp-debug] SMTP полная ошибка (repr):", repr(e), flush=True)
            return 1

        print("[smtp-debug] Готово.", flush=True)
        return 0
    except Exception as e:
        _step("unexpected", False, repr(e))
        traceback.print_exc()
        return 1
    finally:
        if smtp is not None:
            try:
                smtp.quit()
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
