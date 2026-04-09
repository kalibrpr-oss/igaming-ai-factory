"use client";

import {
  approveAdminOrderReview,
  fetchAdminReviewQueue,
  rejectAdminOrderReview,
} from "@/api/endpoints";
import { Button } from "@/components/ui/Button";
import { adminUserDetailPath } from "@/lib/admin-user-detail-path";
import type { AdminReviewOrderRow } from "@/types/admin";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

export default function AdminReviewQueuePage() {
  const [rows, setRows] = useState<AdminReviewOrderRow[] | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [notesByOrder, setNotesByOrder] = useState<Record<number, string>>({});
  const [busyId, setBusyId] = useState<number | null>(null);

  const load = useCallback(() => {
    fetchAdminReviewQueue()
      .then(setRows)
      .catch(
        (e) =>
          setErr(e instanceof Error ? e.message : "Не удалось загрузить очередь")
      );
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  function noteFor(id: number): string | null {
    const t = (notesByOrder[id] ?? "").trim();
    return t.length ? t : null;
  }

  async function approve(id: number) {
    setBusyId(id);
    setErr(null);
    try {
      await approveAdminOrderReview(id, noteFor(id));
      setNotesByOrder((m) => {
        const next = { ...m };
        delete next[id];
        return next;
      });
      load();
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Ошибка одобрения");
    } finally {
      setBusyId(null);
    }
  }

  async function reject(id: number) {
    setBusyId(id);
    setErr(null);
    try {
      await rejectAdminOrderReview(id, noteFor(id));
      setNotesByOrder((m) => {
        const next = { ...m };
        delete next[id];
        return next;
      });
      load();
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Ошибка отклонения");
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-12 md:py-16">
      <h1 className="text-3xl font-semibold tracking-tight text-white md:text-4xl">
        Модерация текстов
      </h1>
      <p className="mt-2 max-w-2xl text-base text-zinc-500">
        Заказы в статусе «на модерации». Одобрить — готово клиенту; отклонить —
        вернётся в «оплачен», можно снова запустить генерацию.
      </p>

      {err && (
        <p className="mt-6 rounded-xl border border-red-500/30 bg-red-500/10 px-5 py-4 text-red-200">
          {err}
        </p>
      )}

      <div className="mt-8 flex gap-3">
        <Button type="button" variant="outline" onClick={() => load()}>
          Обновить
        </Button>
      </div>

      <div className="mt-8 space-y-6">
        {rows === null ? (
          <p className="text-zinc-500">Загрузка…</p>
        ) : rows.length === 0 ? (
          <p className="rounded-2xl border border-white/[0.08] bg-white/[0.02] px-6 py-10 text-center text-zinc-500">
            Очередь пуста — нет заказов на модерации.
          </p>
        ) : (
          rows.map((o) => (
            <div
              key={o.id}
              className="rounded-2xl border border-white/[0.08] bg-white/[0.03] p-6 md:p-8"
            >
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p className="font-mono text-sm text-zinc-500">#{o.id}</p>
                  <h2 className="mt-1 text-xl font-semibold text-white">
                    {o.brand_name}
                  </h2>
                  <p className="mt-2 text-sm text-zinc-500">
                    Пользователь:{" "}
                    <Link
                      href={adminUserDetailPath(o.user_id)}
                      className="text-gem-bright hover:underline"
                    >
                      user #{o.user_id}
                    </Link>
                    {" · "}
                    {o.target_word_count.toLocaleString("ru-RU")} слов ·{" "}
                    <span className="tabular-nums text-zinc-300">
                      {(o.price_cents / 100).toLocaleString("ru-RU")} ₽
                    </span>
                  </p>
                  <p className="mt-1 text-xs text-zinc-600">
                    Обновлён:{" "}
                    {new Date(o.updated_at).toLocaleString("ru-RU")}
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Button
                    type="button"
                    variant="primary"
                    disabled={busyId !== null}
                    onClick={() => void approve(o.id)}
                  >
                    {busyId === o.id ? "…" : "Одобрить"}
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    disabled={busyId !== null}
                    onClick={() => void reject(o.id)}
                  >
                    {busyId === o.id ? "…" : "Отклонить"}
                  </Button>
                </div>
              </div>
              <label className="mt-4 block text-sm text-zinc-500">
                Комментарий модератора (необязательно)
                <textarea
                  value={notesByOrder[o.id] ?? ""}
                  onChange={(e) =>
                    setNotesByOrder((m) => ({ ...m, [o.id]: e.target.value }))
                  }
                  rows={2}
                  disabled={busyId !== null}
                  className="mt-1.5 w-full max-w-xl rounded-xl border border-white/10 bg-black/30 px-4 py-3 text-base text-white outline-none focus:border-violet-500/40"
                  placeholder="Заметка для истории заказа…"
                />
              </label>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
