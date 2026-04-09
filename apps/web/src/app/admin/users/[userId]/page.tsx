"use client";

import {
  fetchAdminUserDetail,
  fetchMe,
  grantAdminCredits,
  patchAdminUserActive,
} from "@/api/endpoints";
import { Button } from "@/components/ui/Button";
import type { AdminUserDetail } from "@/types/admin";
import type { OrderStatus } from "@/types";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

const orderStatusRu: Record<OrderStatus, string> = {
  draft: "Черновик",
  pending_payment: "Ждёт оплаты",
  paid: "Оплачен",
  generating: "Генерация",
  review_required: "На модерации",
  completed: "Готов",
  failed: "Ошибка",
  cancelled: "Отменён",
};

function deviceRu(kind: string): string {
  if (kind === "mobile") return "Телефон / планшет (оценка по UA)";
  if (kind === "desktop") return "ПК (оценка по UA)";
  return "Неизвестно";
}

export default function AdminUserDetailPage() {
  const params = useParams();
  const rawId = params.userId;
  const userId =
    typeof rawId === "string" ? parseInt(rawId, 10) : Number.NaN;

  const [detail, setDetail] = useState<AdminUserDetail | null>(null);
  const [myId, setMyId] = useState<number | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [rubStr, setRubStr] = useState("");
  const [reason, setReason] = useState("");
  const [grantMsg, setGrantMsg] = useState<string | null>(null);

  const load = useCallback(() => {
    if (!Number.isFinite(userId)) return;
    fetchAdminUserDetail(userId)
      .then(setDetail)
      .catch(
        (e) =>
          setErr(e instanceof Error ? e.message : "Не удалось загрузить карточку")
      );
  }, [userId]);

  useEffect(() => {
    fetchMe()
      .then((m) => setMyId(m.id))
      .catch(() => setMyId(null));
  }, []);

  useEffect(() => {
    setErr(null);
    setDetail(null);
    load();
  }, [load]);

  async function toggleActive() {
    if (!detail) return;
    setBusy(true);
    setErr(null);
    try {
      const next = !detail.is_active;
      const row = await patchAdminUserActive(detail.id, next);
      setDetail((d) =>
        d ? { ...d, is_active: row.is_active } : d
      );
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Ошибка");
    } finally {
      setBusy(false);
    }
  }

  async function submitGrant(e: React.FormEvent) {
    e.preventDefault();
    if (!detail) return;
    const rub = parseFloat(rubStr.replace(",", "."));
    if (!Number.isFinite(rub) || rub <= 0) {
      setGrantMsg("Введите сумму в рублях больше нуля");
      return;
    }
    const trimmed = reason.trim();
    if (!trimmed) {
      setGrantMsg("Укажите причину выдачи");
      return;
    }
    const cents = Math.round(rub * 100);
    setBusy(true);
    setGrantMsg(null);
    setErr(null);
    try {
      const res = await grantAdminCredits(detail.id, cents, trimmed);
      setDetail((d) =>
        d ? { ...d, balance_cents: res.new_balance_cents } : d
      );
      setRubStr("");
      setReason("");
      setGrantMsg(
        `Зачислено. Новый баланс: ${(res.new_balance_cents / 100).toLocaleString("ru-RU")} ₽`
      );
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Ошибка выдачи");
    } finally {
      setBusy(false);
    }
  }

  if (!Number.isFinite(userId)) {
    return (
      <div className="mx-auto max-w-6xl px-4 py-16 text-zinc-500">
        Некорректный ID
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-12 md:py-16">
      <div className="flex flex-wrap items-center gap-4">
        <Button variant="outline" type="button" href="/admin/users">
          ← К списку
        </Button>
      </div>

      {err && (
        <p className="mt-6 rounded-xl border border-red-500/30 bg-red-500/10 px-5 py-4 text-red-200">
          {err}
        </p>
      )}

      {detail === null ? (
        <p className="mt-10 text-zinc-500">Загрузка…</p>
      ) : (
        <>
          <h1 className="mt-8 text-3xl font-semibold tracking-tight text-white md:text-4xl">
            {detail.username}
          </h1>
          <p className="mt-1 text-zinc-500">{detail.email}</p>

          <div className="mt-8 grid gap-4 md:grid-cols-2">
            <div className="rounded-2xl border border-white/[0.08] bg-white/[0.03] p-5">
              <p className="text-xs font-medium uppercase tracking-wider text-zinc-500">
                Баланс (Credits)
              </p>
              <p className="mt-2 text-3xl font-semibold tabular-nums text-emerald-200">
                {(detail.balance_cents / 100).toLocaleString("ru-RU")} ₽
              </p>
              <p className="mt-3 text-sm text-zinc-500">
                Email подтверждён: {detail.is_email_verified ? "да" : "нет"}
              </p>
              <p className="mt-1 text-sm text-zinc-500">
                Реф. код: {detail.referral_code ?? "—"}; slug зафиксирован:{" "}
                {detail.referral_slug_locked ? "да" : "нет"}
              </p>
            </div>
            <div className="rounded-2xl border border-white/[0.08] bg-white/[0.03] p-5">
              <p className="text-xs font-medium uppercase tracking-wider text-zinc-500">
                Активность
              </p>
              <p className="mt-2 text-sm text-zinc-300">
                Последний визит:{" "}
                {detail.last_seen_at
                  ? new Date(detail.last_seen_at).toLocaleString("ru-RU")
                  : "нет данных"}
              </p>
              <p className="mt-2 text-sm text-zinc-400">
                Устройство: {deviceRu(detail.last_device_kind)}
              </p>
              <p className="mt-3 text-sm text-zinc-500">
                Награды с рефералок (сумма):{" "}
                <span className="tabular-nums text-zinc-300">
                  {(detail.referral_rewards_total_cents / 100).toLocaleString(
                    "ru-RU"
                  )}{" "}
                  ₽
                </span>
              </p>
            </div>
          </div>

          <div className="mt-8 flex flex-wrap gap-3">
            <Button
              variant="outline"
              type="button"
              disabled={busy || detail.id === myId}
              onClick={() => void toggleActive()}
            >
              {detail.is_active ? "Заблокировать" : "Разблокировать"}
            </Button>
            {detail.id === myId && (
              <span className="self-center text-sm text-zinc-500">
                Себя отключить нельзя
              </span>
            )}
          </div>

          <form
            onSubmit={(e) => void submitGrant(e)}
            className="mt-10 max-w-xl rounded-2xl border border-white/[0.08] bg-white/[0.03] p-6"
          >
            <h2 className="text-lg font-medium text-white">Выдача Credits</h2>
            <p className="mt-1 text-sm text-zinc-500">
              Создаётся проводка adjustment с причиной в журнале (поле note).
            </p>
            <label className="mt-4 block text-sm text-zinc-400">
              Сумма, ₽
              <input
                type="text"
                inputMode="decimal"
                value={rubStr}
                onChange={(e) => setRubStr(e.target.value)}
                className="mt-1.5 w-full rounded-xl border border-white/10 bg-black/30 px-4 py-3 text-base text-white outline-none focus:border-gem-bright/40"
                placeholder="1000"
                disabled={busy}
              />
            </label>
            <label className="mt-4 block text-sm text-zinc-400">
              Причина (видна в проводке)
              <textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                rows={3}
                className="mt-1.5 w-full resize-y rounded-xl border border-white/10 bg-black/30 px-4 py-3 text-base text-white outline-none focus:border-gem-bright/40"
                placeholder="Бонус за обзор, компенсация, акция…"
                disabled={busy}
              />
            </label>
            <div className="mt-5">
              <Button type="submit" variant="primary" disabled={busy}>
                Зачислить
              </Button>
            </div>
            {grantMsg && (
              <p className="mt-4 text-sm text-emerald-200/90">{grantMsg}</p>
            )}
          </form>

          <section className="mt-12">
            <h2 className="text-xl font-medium text-white">Пригласивший</h2>
            {detail.referrer ? (
              <p className="mt-2 text-zinc-300">
                <Link
                  href={`/admin/users/${detail.referrer.id}`}
                  className="text-gem-bright hover:underline"
                >
                  {detail.referrer.username}
                </Link>{" "}
                <span className="text-zinc-500">({detail.referrer.email})</span>
              </p>
            ) : (
              <p className="mt-2 text-zinc-500">Нет</p>
            )}
          </section>

          <section className="mt-10">
            <h2 className="text-xl font-medium text-white">
              Рефералы ({detail.referrals.length})
            </h2>
            <div className="mt-4 overflow-x-auto rounded-2xl border border-white/[0.08]">
              <table className="w-full min-w-[480px] text-left text-sm">
                <thead className="border-b border-white/[0.08] bg-white/[0.03] text-zinc-500">
                  <tr>
                    <th className="px-4 py-2 font-medium">ID</th>
                    <th className="px-4 py-2 font-medium">Username</th>
                    <th className="px-4 py-2 font-medium">Регистрация</th>
                  </tr>
                </thead>
                <tbody>
                  {detail.referrals.length === 0 ? (
                    <tr>
                      <td
                        colSpan={3}
                        className="px-4 py-8 text-center text-zinc-500"
                      >
                        Пока никого не привёл
                      </td>
                    </tr>
                  ) : (
                    detail.referrals.map((r) => (
                      <tr
                        key={r.id}
                        className="border-b border-white/[0.05] text-zinc-300"
                      >
                        <td className="px-4 py-2 font-mono text-xs">
                          <Link
                            href={`/admin/users/${r.id}`}
                            className="text-gem-bright hover:underline"
                          >
                            {r.id}
                          </Link>
                        </td>
                        <td className="px-4 py-2">{r.username}</td>
                        <td className="px-4 py-2 text-xs text-zinc-500">
                          {new Date(r.created_at).toLocaleString("ru-RU")}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </section>

          <section className="mt-10">
            <h2 className="text-xl font-medium text-white">Заказы</h2>
            <div className="mt-4 overflow-x-auto rounded-2xl border border-white/[0.08]">
              <table className="w-full min-w-[640px] text-left text-sm">
                <thead className="border-b border-white/[0.08] bg-white/[0.03] text-zinc-500">
                  <tr>
                    <th className="px-4 py-2 font-medium">#</th>
                    <th className="px-4 py-2 font-medium">Бренд</th>
                    <th className="px-4 py-2 font-medium">Статус</th>
                    <th className="px-4 py-2 font-medium">Цена</th>
                    <th className="px-4 py-2 font-medium">Создан</th>
                  </tr>
                </thead>
                <tbody>
                  {detail.orders.length === 0 ? (
                    <tr>
                      <td
                        colSpan={5}
                        className="px-4 py-8 text-center text-zinc-500"
                      >
                        Заказов нет
                      </td>
                    </tr>
                  ) : (
                    detail.orders.map((o) => (
                      <tr
                        key={o.id}
                        className="border-b border-white/[0.05] text-zinc-300"
                      >
                        <td className="px-4 py-2 font-mono text-xs">{o.id}</td>
                        <td className="px-4 py-2">{o.brand_name}</td>
                        <td className="px-4 py-2">
                          {orderStatusRu[o.status as OrderStatus] ?? o.status}
                        </td>
                        <td className="px-4 py-2 tabular-nums">
                          {(o.price_cents / 100).toLocaleString("ru-RU")} ₽
                        </td>
                        <td className="px-4 py-2 text-xs text-zinc-500">
                          {new Date(o.created_at).toLocaleString("ru-RU")}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </div>
  );
}
