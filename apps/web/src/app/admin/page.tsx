"use client";

import Link from "next/link";

export default function AdminHomePage() {
  return (
    <div className="mx-auto max-w-6xl px-4 py-12 md:py-16">
      <h1 className="text-3xl font-semibold tracking-tight text-white md:text-4xl">
        Панель владельца
      </h1>
      <p className="mt-2 max-w-xl text-base text-zinc-500">
        Список пользователей, карточки, платежи. Пароли не показываем — только
        блокировка и выдача Credits с причиной в проводке.
      </p>
      <div className="mt-10 grid gap-4 sm:grid-cols-2">
        <Link
          href="/admin/users"
          className="rounded-2xl border border-white/[0.08] bg-white/[0.03] p-6 transition-colors hover:border-white/[0.14] hover:bg-white/[0.05]"
        >
          <h2 className="text-lg font-medium text-white">Пользователи</h2>
          <p className="mt-2 text-sm text-zinc-500">
            Регистрации, активность, последнее устройство, бан, выдача баланса
          </p>
        </Link>
        <Link
          href="/admin/payments"
          className="rounded-2xl border border-white/[0.08] bg-white/[0.03] p-6 transition-colors hover:border-white/[0.14] hover:bg-white/[0.05]"
        >
          <h2 className="text-lg font-medium text-white">Платежи</h2>
          <p className="mt-2 text-sm text-zinc-500">
            Лента пополнений и оплат заказов (до 200 последних записей)
          </p>
        </Link>
      </div>
    </div>
  );
}
