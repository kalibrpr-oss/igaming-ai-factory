"use client";

import { loginUser } from "@/api/endpoints";
import { Button } from "@/components/ui/Button";
import { completeAuthSuccess } from "@/lib/auth-storage";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";

function LoginBody() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const verifiedOk = searchParams.get("verified") === "1";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    setLoading(true);
    try {
      const emailNorm = email.trim().toLowerCase();
      const tok = await loginUser({ email: emailNorm, password });
      completeAuthSuccess(router, tok.access_token);
    } catch (er) {
      setErr(er instanceof Error ? er.message : "Ошибка входа");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-lg px-4 py-20">
      <div className="glass-panel p-10 md:p-12">
        <h1 className="text-3xl font-semibold tracking-tight text-white md:text-4xl">
          Вход
        </h1>
        <p className="mt-3 text-base text-zinc-500">
          Нет аккаунта?{" "}
          <Link href="/register" className="text-gem-bright hover:underline">
            Регистрация
          </Link>
        </p>
        <p className="mt-3 rounded-xl border border-emerald-500/25 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-100/90">
          Первый оплаченный заказ — со скидкой <strong>30%</strong> (пока бонус не
          использован).
        </p>
        {verifiedOk && (
          <p className="mt-6 rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-base text-emerald-200">
            Email подтверждён. Войдите с паролем.
          </p>
        )}
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
            Пароль
            <input
              type="password"
              autoComplete="current-password"
              className="mt-2 w-full rounded-xl border border-white/10 bg-ink-900/80 px-4 py-3 text-base text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </label>
          <p className="text-sm text-zinc-500">
            Нет письма? Проверьте спам. Код вводится на{" "}
            <Link href="/verify-email" className="text-gem-bright hover:underline">
              странице подтверждения
            </Link>
            .
          </p>
          {err && <p className="text-base text-red-400">{err}</p>}
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "Входим…" : "Войти"}
          </Button>
        </form>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <div className="mx-auto max-w-lg px-4 py-20 text-center text-zinc-500">
          Загрузка…
        </div>
      }
    >
      <LoginBody />
    </Suspense>
  );
}
