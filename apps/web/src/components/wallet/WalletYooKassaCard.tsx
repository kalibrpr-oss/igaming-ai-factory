"use client";

import {
  createYooKassaWalletTopup,
  fetchYooKassaWalletStatus,
} from "@/api/endpoints";
import { Button } from "@/components/ui/Button";
import { useEffect, useState } from "react";

/** Пополнение через ЮKassa (если на бэкенде заданы ключи). */
export function WalletYooKassaCard() {
  const [available, setAvailable] = useState<boolean | null>(null);
  const [rub, setRub] = useState("500");
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchYooKassaWalletStatus()
      .then((s) => setAvailable(s.yookassa_topup_available))
      .catch(() => setAvailable(false));
  }, []);

  if (available === false || available === null) {
    return null;
  }

  async function pay() {
    setErr(null);
    const n = Number(rub.replace(",", "."));
    if (!Number.isFinite(n) || n <= 0) {
      setErr("Укажите сумму в рублях");
      return;
    }
    const cents = Math.round(n * 100);
    if (cents < 100) {
      setErr("Минимум 1 ₽");
      return;
    }
    setLoading(true);
    try {
      const res = await createYooKassaWalletTopup(cents);
      window.location.href = res.confirmation_url;
    } catch (e) {
      setErr(
        e instanceof Error
          ? e.message
          : "Не удалось создать платёж. Проверь ключи ЮKassa и сеть."
      );
      setLoading(false);
    }
  }

  return (
    <div className="mt-6 rounded-2xl border border-emerald-500/25 bg-emerald-500/5 px-5 py-5">
      <p className="text-sm font-medium text-emerald-200/90">
        Пополнение картой (ЮKassa)
      </p>
      <p className="mt-1 text-sm text-zinc-500">
        Откроется страница оплаты ЮKassa; после успешной оплаты — возврат в кабинет.
      </p>
      <div className="mt-4 flex flex-wrap items-end gap-3">
        <label className="text-base text-zinc-400">
          Сумма, ₽
          <input
            type="text"
            inputMode="decimal"
            className="mt-1 block w-36 rounded-xl border border-white/10 bg-ink-900/80 px-4 py-2.5 text-base text-white outline-none focus:ring-2 focus:ring-emerald-500/30"
            value={rub}
            onChange={(e) => setRub(e.target.value)}
          />
        </label>
        <Button type="button" disabled={loading} onClick={() => void pay()}>
          {loading ? "Создаём платёж…" : "Перейти к оплате"}
        </Button>
      </div>
      {err && <p className="mt-3 text-sm text-red-400">{err}</p>}
    </div>
  );
}
