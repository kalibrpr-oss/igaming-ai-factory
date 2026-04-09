"use client";

import { Button } from "@/components/ui/Button";
import { getToken } from "@/lib/auth-storage";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

export function Header() {
  const path = usePathname();
  const [authed, setAuthed] = useState(false);

  useEffect(() => {
    setAuthed(!!getToken());
  }, [path]);

  return (
    <header className="sticky top-0 z-50 px-4 pt-4">
      <div className="mx-auto flex min-h-[4rem] max-w-6xl items-center justify-between rounded-full border border-white/10 bg-[rgba(8,6,18,0.55)] px-4 py-2.5 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.08)] backdrop-blur-xl md:px-6">
        <Link
          href="/"
          className="pl-1 text-lg font-semibold tracking-wide text-white transition-opacity hover:opacity-90 sm:text-xl"
        >
          iGaming <span className="bg-gradient-to-r from-violet-300 to-indigo-300 bg-clip-text text-transparent">AI-Factory</span>
        </Link>
        <nav className="flex items-center gap-1 sm:gap-2">
          <Link
            href="/guide"
            className="hidden rounded-full px-4 py-2.5 text-base font-medium tracking-wide text-slate-400 transition-colors duration-250 hover:text-white sm:inline"
          >
            Инструкция
          </Link>
          <Link
            href="/terms"
            className="hidden rounded-full px-4 py-2.5 text-base font-medium tracking-wide text-slate-400 transition-colors duration-250 hover:text-white md:inline"
          >
            Terms
          </Link>
          {authed ? (
            <>
              <Button variant="ghost" href="/order" className="!min-h-[48px] !rounded-full !px-6 !py-2.5 !text-base">
                Новый заказ
              </Button>
              <Button variant="outline" href="/dashboard" className="!min-h-[48px] !rounded-full !px-6 !py-2.5 !text-base">
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
