"use client";

import { fetchMe, fetchOrders } from "@/api/endpoints";
import { AuthGate } from "@/components/auth/AuthGate";
import { Button } from "@/components/ui/Button";
import { WalletDevTopup } from "@/components/wallet/WalletDevTopup";
import { WalletYooKassaCard } from "@/components/wallet/WalletYooKassaCard";
import { clearToken } from "@/lib/auth-storage";
import type { OrderDto, OrderStatus } from "@/types";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

const statusRu: Record<OrderStatus, string> = {
  draft: "Черновик",
  pending_payment: "Ждёт оплаты",
  paid: "Оплачен",
  generating: "Генерация",
  review_required: "На модерации",
  completed: "Готов",
  failed: "Ошибка",
  cancelled: "Отменён",
};

function DashboardInner() {
  const router = useRouter();
  const [orders, setOrders] = useState<OrderDto[] | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [balanceCents, setBalanceCents] = useState<number | null>(null);
  const [topupHint, setTopupHint] = useState(false);

  const load = useCallback(() => {
    fetchOrders()
      .then(setOrders)
      .catch((e) => setErr(e instanceof Error ? e.message : "Не удалось загрузить заказы"));
  }, []);

  const loadBalance = useCallback(() => {
    fetchMe()
      .then((me) => setBalanceCents(me.balance_cents ?? 0))
      .catch(() => setBalanceCents(null));
  }, []);

  useEffect(() => {
    load();
    loadBalance();
  }, [load, loadBalance]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const q = new URLSearchParams(window.location.search);
    if (q.get("topup") === "yookassa") {
      setTopupHint(true);
      loadBalance();
    }
  }, [loadBalance]);

  function logout() {
    clearToken();
    router.push("/");
    router.refresh();
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-16 md:py-20">
      <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight text-white md:text-4xl">
            Кабинет
          </h1>
          <p className="mt-2 text-base text-zinc-500 md:text-lg">
            История заказов и статусы
            {balanceCents !== null && (
              <span className="mt-1 block text-sm text-zinc-400">
                Баланс:{" "}
                <span className="font-medium text-emerald-200/90">
                  {(balanceCents / 100).toLocaleString("ru-RU")} ₽
                </span>
              </span>
            )}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button href="/order">Новый заказ</Button>
          <Button variant="outline" type="button" onClick={logout}>
            Выйти
          </Button>
        </div>
      </div>

      {err && (
        <p className="mt-6 rounded-xl border border-red-500/30 bg-red-500/10 px-5 py-4 text-base text-red-200">
          {err}
        </p>
      )}

      {topupHint && (
        <p className="mt-6 rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-5 py-4 text-base text-emerald-100">
          Возврат с оплаты: если деньги прошли, баланс обновится через несколько
          секунд. При необходимости обнови страницу.
        </p>
      )}

      <WalletDevTopup
        balanceCents={balanceCents}
        onSuccess={(cents) => {
          setBalanceCents(cents);
          load();
        }}
      />

      <WalletYooKassaCard />

      <div className="mt-12 overflow-x-auto rounded-3xl border border-white/[0.08]">
        <table className="w-full min-w-[640px] text-left text-base">
          <thead className="border-b border-white/[0.08] bg-white/[0.03] text-zinc-500">
            <tr>
              <th className="px-5 py-4 font-medium">#</th>
              <th className="px-5 py-4 font-medium">Бренд</th>
              <th className="px-5 py-4 font-medium">Статус</th>
              <th className="px-5 py-4 font-medium">Слов</th>
              <th className="px-5 py-4 font-medium">Цена</th>
              <th className="px-5 py-4 font-medium">Создан</th>
            </tr>
          </thead>
          <tbody>
            {orders === null ? (
              <tr>
                <td colSpan={6} className="px-5 py-10 text-center text-zinc-500">
                  Загрузка…
                </td>
              </tr>
            ) : orders.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-5 py-10 text-center text-zinc-500">
                  Пока нет заказов.{" "}
                  <Link href="/order" className="text-gem-bright hover:underline">
                    Создать первый
                  </Link>
                </td>
              </tr>
            ) : (
              orders.map((o) => (
                <tr
                  key={o.id}
                  className="border-b border-white/[0.05] text-zinc-300 transition-colors hover:bg-white/[0.02]"
                >
                  <td className="px-5 py-4 font-mono text-sm">{o.id}</td>
                  <td className="px-5 py-4">{o.brand_name}</td>
                  <td className="px-5 py-4">{statusRu[o.status]}</td>
                  <td className="px-5 py-4">{o.target_word_count}</td>
                  <td className="px-5 py-4">
                    {(o.price_cents / 100).toLocaleString("ru-RU")} ₽
                  </td>
                  <td className="px-5 py-4 text-sm text-zinc-500">
                    {new Date(o.created_at).toLocaleString("ru-RU")}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <AuthGate>
      <DashboardInner />
    </AuthGate>
  );
}
