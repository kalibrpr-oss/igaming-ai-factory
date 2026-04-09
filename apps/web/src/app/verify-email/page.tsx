"use client";

import {
  resendVerificationEmailRequest,
  verifyEmailRequest,
} from "@/api/endpoints";
import { Button } from "@/components/ui/Button";
import { completeAuthSuccess } from "@/lib/auth-storage";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";

function mapVerifyError(message: string): string {
  if (message === "Неверный код") {
    return "Код не подошёл. Проверьте цифры и попробуйте снова.";
  }
  if (message === "Код истёк") {
    return "Срок кода закончился. Запросите новый код ниже.";
  }
  if (message === "Код уже использован") {
    return "Этот код уже использован. Запросите новый код ниже.";
  }
  if (message.includes("Слишком много попыток подтверждения")) {
    return "Слишком много попыток. Подождите немного и попробуйте снова.";
  }
  if (message === "Email уже подтверждён") {
    return "Email уже подтверждён. Можно сразу войти в аккаунт.";
  }
  return message;
}

function mapResendError(message: string): string {
  if (message.includes("Слишком частый запрос нового кода")) {
    return message;
  }
  if (message.includes("Слишком много запросов")) {
    return "Слишком много повторных отправок за сегодня. Попробуйте позже.";
  }
  if (message.includes("Не удалось отправить письмо с кодом")) {
    return "Сейчас не удалось отправить письмо. Попробуйте немного позже.";
  }
  if (message === "Неверный email или пароль") {
    return "Проверьте email и пароль от аккаунта, затем повторите.";
  }
  if (message === "Email уже подтверждён") {
    return "Email уже подтверждён. Перейдите на страницу входа.";
  }
  return message;
}

function VerifyEmailBody() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const prefilledEmail = searchParams.get("email") ?? "";
  const flow = searchParams.get("flow") ?? "";

  const [code, setCode] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const [resendEmail, setResendEmail] = useState(prefilledEmail);
  const [resendPassword, setResendPassword] = useState("");
  const [resendErr, setResendErr] = useState<string | null>(null);
  const [resendOk, setResendOk] = useState<string | null>(null);
  const [resendLoading, setResendLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (loading) return;
    setErr(null);
    setLoading(true);
    try {
      const res = await verifyEmailRequest({ code: code.trim() });
      if (!res.access_token) {
        throw new Error("Не удалось открыть сессию. Попробуйте войти вручную.");
      }
      completeAuthSuccess(router, res.access_token);
    } catch (er) {
      if (er instanceof Error) {
        setErr(mapVerifyError(er.message));
      } else {
        setErr("Не удалось подтвердить email. Попробуйте ещё раз.");
      }
    } finally {
      setLoading(false);
    }
  }

  async function onResend(e: React.FormEvent) {
    e.preventDefault();
    if (resendLoading) return;
    setResendErr(null);
    setResendOk(null);
    const email = resendEmail.trim().toLowerCase();
    if (!email) {
      setResendErr("Укажите email");
      return;
    }
    if (!resendPassword) {
      setResendErr("Введите пароль от аккаунта");
      return;
    }
    setResendLoading(true);
    try {
      await resendVerificationEmailRequest({ email, password: resendPassword });
      setResendOk(
        "Новый код отправлен. Проверьте почту и «Спам», затем введите 6 цифр выше."
      );
      setResendPassword("");
    } catch (er) {
      if (er instanceof Error) {
        setResendErr(mapResendError(er.message));
      } else {
        setResendErr("Не удалось отправить код. Попробуйте позже.");
      }
    } finally {
      setResendLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-lg px-4 py-20">
      <div className="glass-panel p-10 md:p-12">
        <h1 className="text-3xl font-semibold tracking-tight text-white md:text-4xl">
          Подтверждение email
        </h1>
        <p className="mt-3 text-base text-zinc-500">
          Введите 6 цифр из письма. Код действует 15 минут. После подтверждения
          вы сразу попадёте в кабинет.
        </p>
        {(flow === "new-register" || flow === "existing-unverified") && (
          <p className="mt-3 text-base text-zinc-400">
            Проверьте почту и введите код. Если письма нет — запросите новый код
            ниже.
          </p>
        )}
        {prefilledEmail ? (
          <p className="mt-4 text-base text-zinc-400">
            Адрес: <span className="text-zinc-200">{prefilledEmail}</span>
          </p>
        ) : (
          <p className="mt-4 text-base text-zinc-500">
            Если вы не переходили с регистрации, укажите тот же email в блоке ниже
            при повторной отправке кода.
          </p>
        )}
        <p className="mt-2 text-sm text-zinc-500">
          <Link href="/register" className="text-gem-bright hover:underline">
            Ошиблись в email? Вернуться к регистрации
          </Link>
        </p>
        <p className="mt-1 text-sm text-zinc-500">
          Если email уже подтверждён, просто переходите на{" "}
          <Link href="/login" className="text-gem-bright hover:underline">
            страницу входа
          </Link>
          .
        </p>
        <form onSubmit={onSubmit} className="mt-10 space-y-5">
          <label className="block text-base text-zinc-400">
            Код из письма (6 цифр)
            <input
              className="mt-2 w-full rounded-xl border border-white/10 bg-ink-900/80 px-4 py-3 font-mono text-2xl tracking-[0.3em] text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
              value={code}
              onChange={(e) => {
                const d = e.target.value.replace(/\D/g, "").slice(0, 6);
                setCode(d);
              }}
              onPaste={(e) => {
                e.preventDefault();
                const text = e.clipboardData.getData("text");
                const d = text.replace(/\D/g, "").slice(0, 6);
                setCode(d);
              }}
              required
              minLength={6}
              maxLength={6}
              inputMode="numeric"
              autoComplete="one-time-code"
              placeholder="000000"
            />
          </label>
          {err && <p className="text-base text-red-400">{err}</p>}
          {err?.includes("Можно сразу войти") && (
            <p className="text-sm text-zinc-400">
              <Link href="/login" className="text-gem-bright hover:underline">
                Перейти ко входу
              </Link>
              .
            </p>
          )}
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "Проверяем…" : "Подтвердить"}
          </Button>
        </form>

        <div className="mt-10 border-t border-white/10 pt-8">
          <p className="text-sm font-medium text-zinc-400">
            Письмо не пришло?
          </p>
          <form onSubmit={onResend} className="mt-4 space-y-4">
            <label className="block text-base text-zinc-400">
              Email
              <input
                type="email"
                autoComplete="email"
                className="mt-2 w-full rounded-xl border border-white/10 bg-ink-900/80 px-4 py-3 text-base text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
                value={resendEmail}
                onChange={(e) => setResendEmail(e.target.value)}
                placeholder="you@example.com"
              />
            </label>
            <label className="block text-base text-zinc-400">
              Пароль от аккаунта
              <input
                type="password"
                autoComplete="current-password"
                className="mt-2 w-full rounded-xl border border-white/10 bg-ink-900/80 px-4 py-3 text-base text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
                value={resendPassword}
                onChange={(e) => setResendPassword(e.target.value)}
                placeholder="••••••••"
              />
            </label>
            {resendErr && (
              <p className="text-base text-red-400">{resendErr}</p>
            )}
            {resendOk && (
              <p className="text-base text-emerald-400/90">{resendOk}</p>
            )}
            <Button
              type="submit"
              variant="outline"
              className="w-full"
              disabled={resendLoading}
            >
              {resendLoading ? "Отправляем…" : "Отправить код повторно"}
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense
      fallback={
        <div className="mx-auto max-w-lg px-4 py-20 text-center text-zinc-500">
          Загрузка…
        </div>
      }
    >
      <VerifyEmailBody />
    </Suspense>
  );
}
