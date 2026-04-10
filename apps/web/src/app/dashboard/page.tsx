"use client";

import { fetchMe, fetchOrder, fetchOrders } from "@/api/endpoints";
import { AuthGate } from "@/components/auth/AuthGate";
import { Button } from "@/components/ui/Button";
import { WalletDevTopup } from "@/components/wallet/WalletDevTopup";
import { ReferralProgramCard } from "@/components/referral/ReferralProgramCard";
import { WalletYooKassaCard } from "@/components/wallet/WalletYooKassaCard";
import { clearToken } from "@/lib/auth-storage";
import type { OrderDto, OrderKind, OrderStatus } from "@/types";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

const orderKindRu: Record<OrderKind, string> = {
  generate: "Генерация",
  uniquify: "Уникализация",
};

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
  const [isAdmin, setIsAdmin] = useState(false);
  const [topupHint, setTopupHint] = useState(false);
  /** Просмотр сгенерированного текста */
  const [textModal, setTextModal] = useState<{
    open: boolean;
    brandName: string;
    orderId: number;
    text: string | null;
    loading: boolean;
    err: string | null;
  }>({
    open: false,
    brandName: "",
    orderId: 0,
    text: null,
    loading: false,
    err: null,
  });

  const load = useCallback(() => {
    fetchOrders()
      .then(setOrders)
      .catch((e) => setErr(e instanceof Error ? e.message : "Не удалось загрузить заказы"));
  }, []);

  const loadBalance = useCallback(() => {
    fetchMe()
      .then((me) => {
        setBalanceCents(me.balance_cents ?? 0);
        setIsAdmin(me.is_admin);
      })
      .catch(() => {
        setBalanceCents(null);
        setIsAdmin(false);
      });
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

  function canViewOrderText(status: OrderStatus): boolean {
    return (
      status === "review_required" ||
      status === "completed" ||
      status === "failed"
    );
  }

  async function openOrderText(o: OrderDto) {
    setTextModal({
      open: true,
      brandName: o.brand_name,
      orderId: o.id,
      text: o.generated_text,
      loading: !o.generated_text,
      err: null,
    });
    if (o.generated_text) return;
    try {
      const fresh = await fetchOrder(o.id);
      setTextModal((m) => ({
        ...m,
        text: fresh.generated_text,
        loading: false,
        err: fresh.generated_text
          ? null
          : "Текст пока недоступен. Обновите страницу или повторите позже.",
      }));
    } catch (e) {
      setTextModal((m) => ({
        ...m,
        loading: false,
        err: e instanceof Error ? e.message : "Не удалось загрузить текст",
      }));
    }
  }

  function closeTextModal() {
    setTextModal((m) => ({ ...m, open: false }));
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-16 md:py-20">
      <div className="flex flex-col gap-6 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight text-white md:text-4xl">
            Кабинет
          </h1>
          <p className="mt-2 text-base text-zinc-500 md:text-lg">
            История заказов и статусы
          </p>
          <div className="mt-5 rounded-2xl border border-white/[0.08] bg-white/[0.03] px-5 py-4 md:px-6 md:py-5">
            <p className="text-sm font-medium uppercase tracking-wider text-zinc-500">
              Баланс
            </p>
            <p className="mt-1 text-4xl font-semibold tabular-nums tracking-tight text-emerald-200 md:text-5xl">
              {balanceCents === null
                ? "…"
                : `${(balanceCents / 100).toLocaleString("ru-RU")} ₽`}
            </p>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button href="/order">Новый заказ</Button>
          {isAdmin && (
            <Button variant="outline" href="/admin">
              Админка
            </Button>
          )}
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
          После успешной оплаты баланс обновится в течение нескольких секунд. При
          необходимости обновите страницу.
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

      <ReferralProgramCard />

      <div className="mt-12 overflow-x-auto rounded-3xl border border-white/[0.08]">
        <table className="w-full min-w-[720px] text-left text-base">
          <thead className="border-b border-white/[0.08] bg-white/[0.03] text-zinc-500">
            <tr>
              <th className="px-5 py-4 font-medium">#</th>
              <th className="px-5 py-4 font-medium">Бренд</th>
              <th className="px-5 py-4 font-medium">Тип</th>
              <th className="px-5 py-4 font-medium">Статус</th>
              <th className="px-5 py-4 font-medium">Слов</th>
              <th className="px-5 py-4 font-medium">Цена</th>
              <th className="px-5 py-4 font-medium">Создан</th>
              <th className="px-5 py-4 font-medium">Текст</th>
            </tr>
          </thead>
          <tbody>
            {orders === null ? (
              <tr>
                <td colSpan={8} className="px-5 py-10 text-center text-zinc-500">
                  Загрузка…
                </td>
              </tr>
            ) : orders.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-5 py-10 text-center text-zinc-500">
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
                  <td className="px-5 py-4 text-sm text-zinc-400">
                    {orderKindRu[(o.order_kind ?? "generate") as OrderKind]}
                  </td>
                  <td className="px-5 py-4">{statusRu[o.status]}</td>
                  <td className="px-5 py-4">{o.target_word_count}</td>
                  <td className="px-5 py-4">
                    {(o.price_cents / 100).toLocaleString("ru-RU")} ₽
                  </td>
                  <td className="px-5 py-4 text-sm text-zinc-500">
                    {new Date(o.created_at).toLocaleString("ru-RU")}
                  </td>
                  <td className="px-5 py-4">
                    {canViewOrderText(o.status) ? (
                      <button
                        type="button"
                        onClick={() => void openOrderText(o)}
                        className="text-sm font-medium text-gem-bright underline decoration-white/20 underline-offset-4 transition-colors duration-200 hover:text-emerald-300"
                      >
                        Посмотреть
                      </button>
                    ) : (
                      <span className="text-sm text-zinc-600">—</span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {textModal.open && (
        <div
          className="fixed inset-0 z-50 flex items-end justify-center bg-black/60 p-4 backdrop-blur-sm sm:items-center"
          role="dialog"
          aria-modal="true"
          aria-labelledby="order-text-modal-title"
          onClick={closeTextModal}
        >
          <div
            className="glass-panel max-h-[85vh] w-full max-w-3xl overflow-hidden rounded-2xl border border-white/10 shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between gap-4 border-b border-white/10 px-6 py-4">
              <div>
                <h2
                  id="order-text-modal-title"
                  className="text-lg font-semibold text-white"
                >
                  Текст заказа #{textModal.orderId}
                </h2>
                <p className="mt-1 text-sm text-zinc-500">{textModal.brandName}</p>
              </div>
              <button
                type="button"
                onClick={closeTextModal}
                className="rounded-lg px-3 py-1.5 text-sm text-zinc-400 transition-colors hover:bg-white/10 hover:text-white"
              >
                Закрыть
              </button>
            </div>
            <div className="max-h-[calc(85vh-5rem)] overflow-y-auto px-6 py-4">
              {textModal.loading && (
                <p className="text-zinc-400">Загружаем текст…</p>
              )}
              {textModal.err && (
                <p className="text-red-300/90">{textModal.err}</p>
              )}
              {!textModal.loading && !textModal.err && textModal.text && (
                <pre className="whitespace-pre-wrap break-words font-sans text-base leading-relaxed text-zinc-200">
                  {textModal.text}
                </pre>
              )}
              {!textModal.loading && !textModal.err && !textModal.text && (
                <p className="text-zinc-500">
                  Текста нет в ответе. Обновите страницу кабинета.
                </p>
              )}
            </div>
          </div>
        </div>
      )}
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
