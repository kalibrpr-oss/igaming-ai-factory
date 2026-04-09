"use client";

import { registerUser } from "@/api/endpoints";
import { Button } from "@/components/ui/Button";
import { PasswordFieldToggle } from "@/components/ui/PasswordFieldToggle";
import { getReferralCookie } from "@/lib/referral-cookie";
import { validateUsername } from "@/lib/username-rules";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

function mapRegisterError(message: string): string {
  if (message === "Email уже зарегистрирован") {
    return "Этот email уже подтверждён. Войдите в аккаунт на странице входа.";
  }
  if (message.includes("Слишком много запросов")) {
    return "Слишком много попыток. Подождите немного и повторите.";
  }
  return message;
}

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [passwordRepeat, setPasswordRepeat] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (loading) return;
    setErr(null);
    const usernameErr = validateUsername(username);
    if (usernameErr) {
      setErr(usernameErr);
      return;
    }
    if (password !== passwordRepeat) {
      setErr("Пароли не совпадают.");
      return;
    }
    setLoading(true);
    try {
      const refCookie = getReferralCookie();
      const res = await registerUser({
        email,
        username,
        password,
        ...(refCookie ? { referral_code: refCookie } : {}),
      });

      const emailNorm = email.trim().toLowerCase();
      const q = new URLSearchParams();
      q.set("email", emailNorm);
      if (res.registration_status === "already_pending_verification") {
        q.set("flow", "existing-unverified");
      } else {
        q.set("flow", "new-register");
      }
      router.push(`/verify-email?${q.toString()}`);
    } catch (er) {
      if (er instanceof Error) {
        setErr(mapRegisterError(er.message));
      } else {
        setErr("Не удалось завершить регистрацию. Попробуйте снова.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-lg px-4 py-20">
      <div className="glass-panel p-10 md:p-12">
        <h1 className="text-3xl font-semibold tracking-tight text-white md:text-4xl">
          Регистрация
        </h1>
        <p className="mt-3 text-base text-zinc-500">
          Уже есть аккаунт?{" "}
          <Link href="/login" className="text-gem-bright hover:underline">
            Войти
          </Link>
        </p>
        <p className="mt-3 rounded-xl border border-emerald-500/25 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-100/90">
          Скидка <strong>30%</strong> на первый оплаченный заказ — после регистрации и
          пополнения баланса.
        </p>
        <p className="mt-3 text-sm text-zinc-500">
          После регистрации откроем подтверждение email. Если письмо не пришло
          сразу, новый код можно запросить там же.
        </p>
        <form onSubmit={onSubmit} className="mt-10 space-y-5">
          <label className="block text-base text-zinc-400">
            Email
            <input
              type="email"
              autoComplete="email"
              className="mt-2 w-full rounded-xl border border-white/10 bg-ink-900/80 px-4 py-3 text-base text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </label>
          <label className="block text-base text-zinc-400">
            Имя пользователя
            <input
              autoComplete="username"
              className="mt-2 w-full rounded-xl border border-white/10 bg-ink-900/80 px-4 py-3 text-base text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              minLength={4}
              maxLength={15}
              pattern="[a-zA-Z0-9]+"
              title="4–15 символов: латинские буквы и цифры"
            />
            <span className="mt-1 block text-sm text-zinc-500">
              От 4 до 15 символов: только английские буквы и цифры.
            </span>
          </label>
          <PasswordFieldToggle
            label="Пароль (мин. 8 символов)"
            value={password}
            onChange={setPassword}
            autoComplete="new-password"
            minLength={8}
            required
          />
          <PasswordFieldToggle
            label="Повторите пароль"
            value={passwordRepeat}
            onChange={setPasswordRepeat}
            autoComplete="new-password"
            minLength={8}
            required
          />
          {err && (
            <p className="text-base text-red-400">{err}</p>
          )}
          {err?.includes("Войдите в аккаунт") && (
            <p className="text-sm text-zinc-400">
              Перейти к{" "}
              <Link href="/login" className="text-gem-bright hover:underline">
                входу
              </Link>
              .
            </p>
          )}
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "Создаём аккаунт…" : "Зарегистрироваться"}
          </Button>
        </form>
      </div>
    </div>
  );
}
