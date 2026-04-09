"use client";

import { fetchAdminUsers } from "@/api/endpoints";
import { adminUserDetailPath } from "@/lib/admin-user-detail-path";
import type { AdminUserRow } from "@/types/admin";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

function deviceRu(kind: string): string {
  if (kind === "mobile") return "Телефон";
  if (kind === "desktop") return "ПК";
  return "—";
}

export default function AdminUsersPage() {
  const [rows, setRows] = useState<AdminUserRow[] | null>(null);
  const [err, setErr] = useState<string | null>(null);

  const load = useCallback(() => {
    fetchAdminUsers()
      .then(setRows)
      .catch(
        (e) =>
          setErr(e instanceof Error ? e.message : "Не удалось загрузить список")
      );
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="mx-auto max-w-6xl px-4 py-12 md:py-16">
      <h1 className="text-3xl font-semibold tracking-tight text-white md:text-4xl">
        Пользователи
      </h1>
      <p className="mt-2 text-zinc-500">
        Сортировка: новые сверху. Активность обновляется при запросах с JWT (не
        чаще раз в ~2 мин).
      </p>

      {err && (
        <p className="mt-6 rounded-xl border border-red-500/30 bg-red-500/10 px-5 py-4 text-red-200">
          {err}
        </p>
      )}

      <div className="mt-8 overflow-x-auto rounded-3xl border border-white/[0.08]">
        <table className="w-full min-w-[900px] text-left text-sm">
          <thead className="border-b border-white/[0.08] bg-white/[0.03] text-zinc-500">
            <tr>
              <th className="px-4 py-3 font-medium">ID</th>
              <th className="px-4 py-3 font-medium">Email</th>
              <th className="px-4 py-3 font-medium">Username</th>
              <th className="px-4 py-3 font-medium">Статус</th>
              <th className="px-4 py-3 font-medium">Заказы</th>
              <th className="px-4 py-3 font-medium">Оплаты ✓</th>
              <th className="px-4 py-3 font-medium">Был онлайн</th>
              <th className="px-4 py-3 font-medium">Устройство</th>
            </tr>
          </thead>
          <tbody>
            {rows === null ? (
              <tr>
                <td colSpan={8} className="px-4 py-12 text-center text-zinc-500">
                  Загрузка…
                </td>
              </tr>
            ) : rows.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-4 py-12 text-center text-zinc-500">
                  Пока нет пользователей
                </td>
              </tr>
            ) : (
              rows.map((u) => (
                <tr
                  key={u.id}
                  className="border-b border-white/[0.05] text-zinc-300 transition-colors hover:bg-white/[0.02]"
                >
                  <td className="px-4 py-3 font-mono text-xs">
                    <Link
                      href={adminUserDetailPath(u.id)}
                      className="text-gem-bright hover:underline"
                    >
                      {u.id}
                    </Link>
                  </td>
                  <td className="px-4 py-3">{u.email}</td>
                  <td className="px-4 py-3">{u.username}</td>
                  <td className="px-4 py-3">
                    {!u.is_active ? (
                      <span className="text-red-300">заблокирован</span>
                    ) : u.is_admin ? (
                      <span className="text-amber-200/90">админ</span>
                    ) : (
                      <span className="text-zinc-500">активен</span>
                    )}
                  </td>
                  <td className="px-4 py-3 tabular-nums">{u.orders_total}</td>
                  <td className="px-4 py-3 tabular-nums">
                    {u.payments_succeeded}
                  </td>
                  <td className="px-4 py-3 text-xs text-zinc-500">
                    {u.last_seen_at
                      ? new Date(u.last_seen_at).toLocaleString("ru-RU")
                      : "—"}
                  </td>
                  <td className="px-4 py-3 text-zinc-400">
                    {deviceRu(u.last_device_kind)}
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
