"use client";

import { Button } from "@/components/ui/Button";
import { getToken } from "@/lib/auth-storage";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

/** Нижний блок CTA на главной: для залогиненных — без «Создать аккаунт». */
export function HomeBottomCta() {
  const path = usePathname();
  const [authed, setAuthed] = useState(false);

  useEffect(() => {
    setAuthed(!!getToken());
  }, [path]);

  if (authed) {
    return (
      <section className="px-4 pb-28">
        <div className="liquid-glass mx-auto max-w-4xl p-10 text-center shadow-emerald-glow md:p-12">
          <h2 className="text-3xl font-semibold text-white md:text-4xl">
            С возвращением
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-base text-zinc-400 md:text-lg">
            Кабинет: заказы, баланс, статусы генерации.
          </p>
          <div className="mt-10 flex flex-wrap justify-center gap-4">
            <Button href="/dashboard" primaryCta>
              Открыть кабинет
            </Button>
            <Button variant="outline" href="/order">
              Новый заказ
            </Button>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="px-4 pb-28">
      <div className="liquid-glass mx-auto max-w-4xl p-10 text-center shadow-emerald-glow md:p-12">
        <h2 className="text-3xl font-semibold text-white md:text-4xl">
          Первый заказ
        </h2>
        <p className="mx-auto mt-4 max-w-2xl text-base text-zinc-400 md:text-lg">
          Регистрация, подтверждение почты, затем форма заказа и оплата с баланса.
        </p>
        <div className="mt-10 flex flex-wrap justify-center gap-4">
          <Button href="/register" primaryCta>
            Создать аккаунт
          </Button>
          <Button variant="outline" href="/order">
            Вход и заказ
          </Button>
        </div>
      </div>
    </section>
  );
}
