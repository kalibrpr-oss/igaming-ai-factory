"use client";

import { mockUserWalletTopup } from "@/api/endpoints";
import { Button } from "@/components/ui/Button";
import { useState } from "react";

const ENABLED =
  typeof process.env.NEXT_PUBLIC_ENABLE_WALLET_MOCK === "string" &&
  process.env.NEXT_PUBLIC_ENABLE_WALLET_MOCK === "true";

type Props = {
  balanceCents: number | null;
  onSuccess: (newBalanceCents: number) => void;
};

/** Блок только для локальной разработки (см. backend ENABLE_USER_WALLET_MOCK_TOPUP). */
export function WalletDevTopup({ balanceCents, onSuccess }: Props) {
  const [rub, setRub] = useState("500");
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (!ENABLED) return null;

  async function submit() {
    setErr(null);
    const n = Number(rub.replace(",", "."));
    if (!Number.isFinite(n) || n <= 0) {
      setErr("Введи сумму в рублях");
      return;
    }
    const cents = Math.round(n * 100);
    if (cents < 100) {
      setErr("Минимум 1 ₽");
      return;
    }
    setLoading(true);
    try {
      const res = await mockUserWalletTopup(cents);
      onSuccess(res.user_balance_cents);
      setRub("500");
    } catch (e) {
      setErr(
        e instanceof Error ? e.message : "Пополнение недоступно (проверь флаг на сервере)."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mt-10 rounded-2xl border border-amber-500/25 bg-amber-500/5 px-5 py-5">
      <p className="text-sm font-medium text-amber-200/90">Тестовое пополнение баланса</p>
      <p className="mt-1 text-sm text-zinc-500">
        Только локальная разработка. На проде выключено.
      </p>
      <div className="mt-4 flex flex-wrap items-end gap-3">
        <label className="text-base text-zinc-400">
          Сумма, ₽
          <input
            type="text"
            inputMode="decimal"
            className="mt-1 block w-36 rounded-xl border border-white/10 bg-ink-900/80 px-4 py-2.5 text-base text-white outline-none focus:ring-2 focus:ring-amber-500/30"
            value={rub}
            onChange={(e) => setRub(e.target.value)}
          />
        </label>
        <Button type="button" variant="outline" disabled={loading} onClick={() => void submit()}>
          {loading ? "…" : "Зачислить"}
        </Button>
      </div>
      {balanceCents !== null && (
        <p className="mt-3 text-sm text-zinc-400">
          Текущий баланс:{" "}
          <span className="text-zinc-200">
            {(balanceCents / 100).toLocaleString("ru-RU")} ₽
          </span>
        </p>
      )}
      {err && <p className="mt-3 text-sm text-red-400">{err}</p>}
    </div>
  );
}
