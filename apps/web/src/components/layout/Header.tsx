"use client";

import { fetchMe } from "@/api/endpoints";
import { Button } from "@/components/ui/Button";
import { getToken } from "@/lib/auth-storage";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

export function Header() {
  const path = usePathname();
  const [authed, setAuthed] = useState(false);
  const [balanceCents, setBalanceCents] = useState<number | null>(null);

  useEffect(() => {
    setAuthed(!!getToken());
  }, [path]);

  const loadBalance = useCallback(() => {
    if (!getToken()) {
      setBalanceCents(null);
      return;
    }
    fetchMe()
      .then((me) => setBalanceCents(me.balance_cents ?? 0))
      .catch(() => setBalanceCents(null));
  }, []);

  useEffect(() => {
    if (!authed) {
      setBalanceCents(null);
      return;
    }
    loadBalance();
  }, [authed, path, loadBalance]);

  useEffect(() => {
    if (!authed || typeof document === "undefined") return;
    const onVis = () => {
      if (document.visibilityState === "visible") loadBalance();
    };
    document.addEventListener("visibilitychange", onVis);
    return () => document.removeEventListener("visibilitychange", onVis);
  }, [authed, loadBalance]);

  return (
    <header className="sticky top-0 z-50 px-4 pt-2 sm:pt-3">
      <div className="mx-auto flex min-h-[4rem] max-w-6xl items-center justify-between gap-2 rounded-full border border-white/10 bg-[rgba(8,6,18,0.55)] px-3 py-2 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.08)] backdrop-blur-xl sm:px-4 sm:py-2.5 md:px-6">
        <Link
          href="/"
          className="min-w-0 shrink pl-0.5 text-base font-semibold tracking-wide text-white transition-opacity hover:opacity-90 sm:pl-1 sm:text-lg md:text-xl"
        >
          iGaming <span className="bg-gradient-to-r from-violet-300 to-indigo-300 bg-clip-text text-transparent">AI-Factory</span>
        </Link>
        <nav className="flex min-w-0 flex-1 items-center justify-end gap-1 sm:gap-2">
          <Link
            href="/guide"
            className="hidden rounded-full px-4 py-2.5 text-base font-medium tracking-wide text-slate-400 transition-colors duration-250 hover:text-white sm:inline"
          >
            Инструкция
          </Link>
          {authed ? (
            <>
              <Link
                href="/dashboard"
                className="hidden shrink-0 items-center gap-2 rounded-full border border-gem-bright/25 bg-emerald-950/35 px-3 py-2 text-sm tabular-nums text-gem-mist shadow-emerald-glow backdrop-blur-sm transition-colors hover:border-gem-bright/45 hover:bg-emerald-950/50 sm:inline-flex md:px-4 md:text-base"
                title="Баланс в кабинете"
              >
                <span className="hidden text-xs font-medium text-zinc-400 md:inline">
                  Баланс
                </span>
                <span className="font-semibold text-gem-bright">
                  {balanceCents === null
                    ? "…"
                    : `${(balanceCents / 100).toLocaleString("ru-RU")} ₽`}
                </span>
              </Link>
              <Link
                href="/dashboard"
                className="inline-flex shrink-0 items-center rounded-full border border-gem-bright/25 bg-emerald-950/35 px-2.5 py-2 text-xs font-semibold tabular-nums text-gem-bright shadow-emerald-glow backdrop-blur-sm sm:hidden"
                title="Баланс в кабинете"
              >
                {balanceCents === null
                  ? "…"
                  : `${(balanceCents / 100).toLocaleString("ru-RU")} ₽`}
              </Link>
              <Button variant="ghost" href="/order" className="!min-h-[48px] !rounded-full !px-6 !py-2.5 !text-base">
                Новый заказ
              </Button>
              <Button href="/dashboard" className="!min-h-[48px] !rounded-full !px-6 !py-2.5 !text-base">
                Кабинет
              </Button>
            </>
          ) : (
            <>
              <Button variant="ghost" href="/login" className="!min-h-[48px] !rounded-full !px-6 !py-2.5 !text-base">
                Вход
              </Button>
              <Button href="/register" className="!min-h-[48px] !rounded-full !px-6 !py-2.5 !text-base">
                Регистрация
              </Button>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
