"use client";

import { fetchAdminPayments } from "@/api/endpoints";
import type { AdminPaymentRow } from "@/types/admin";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

const paymentStatusRu: Record<string, string> = {
  pending: "В процессе",
  succeeded: "Успешно",
  failed: "Ошибка",
  refunded: "Возврат",
};

const paymentKindRu: Record<string, string> = {
  wallet_topup: "Пополнение",
  order_payment: "Заказ",
};

export default function AdminPaymentsPage() {
  const [rows, setRows] = useState<AdminPaymentRow[] | null>(null);
  const [err, setErr] = useState<string | null>(null);

  const load = useCallback(() => {
    fetchAdminPayments()
      .then(setRows)
      .catch(
        (e) =>
          setErr(e instanceof Error ? e.message : "Не удалось загрузить платежи")
      );
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="mx-auto max-w-6xl px-4 py-12 md:py-16">
      <h1 className="text-3xl font-semibold tracking-tight text-white md:text-4xl">
        Платежи
      </h1>
      <p className="mt-2 text-zinc-500">
        До 200 последних записей: сумма в рублях, провайдер, статус.
      </p>

      {err && (
        <p className="mt-6 rounded-xl border border-red-500/30 bg-red-500/10 px-5 py-4 text-red-200">
          {err}
        </p>
      )}

      <div className="mt-8 overflow-x-auto rounded-3xl border border-white/[0.08]">
        <table className="w-full min-w-[960px] text-left text-sm">
          <thead className="border-b border-white/[0.08] bg-white/[0.03] text-zinc-500">
            <tr>
              <th className="px-4 py-3 font-medium">ID</th>
              <th className="px-4 py-3 font-medium">Пользователь</th>
              <th className="px-4 py-3 font-medium">Тип</th>
              <th className="px-4 py-3 font-medium">Провайдер</th>
              <th className="px-4 py-3 font-medium">Сумма</th>
              <th className="px-4 py-3 font-medium">Статус</th>
              <th className="px-4 py-3 font-medium">Создан</th>
            </tr>
          </thead>
          <tbody>
            {rows === null ? (
              <tr>
                <td colSpan={7} className="px-4 py-12 text-center text-zinc-500">
                  Загрузка…
                </td>
              </tr>
            ) : rows.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-12 text-center text-zinc-500">
                  Платежей пока нет
                </td>
              </tr>
            ) : (
              rows.map((p) => (
                <tr
                  key={p.id}
                  className="border-b border-white/[0.05] text-zinc-300 transition-colors hover:bg-white/[0.02]"
                >
                  <td className="px-4 py-3 font-mono text-xs">{p.id}</td>
                  <td className="px-4 py-3">
                    <Link
                      href={`/admin/users/${p.user_id}`}
                      className="text-gem-bright hover:underline"
                    >
                      {p.user_username}
                    </Link>
                    <div className="text-xs text-zinc-500">{p.user_email}</div>
                  </td>
                  <td className="px-4 py-3 text-zinc-400">
                    {paymentKindRu[p.kind] ?? p.kind}
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-zinc-400">
                    {p.provider}
                  </td>
                  <td className="px-4 py-3 tabular-nums">
                    {(p.amount_cents / 100).toLocaleString("ru-RU")} {p.currency}
                  </td>
                  <td className="px-4 py-3">
                    {paymentStatusRu[p.status] ?? p.status}
                  </td>
                  <td className="px-4 py-3 text-xs text-zinc-500">
                    {new Date(p.created_at).toLocaleString("ru-RU")}
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
