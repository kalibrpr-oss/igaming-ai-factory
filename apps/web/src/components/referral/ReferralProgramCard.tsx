"use client";

import {
  fetchReferralSummary,
  updateReferralCode,
  type ReferralSummary,
} from "@/api/endpoints";
import { Button } from "@/components/ui/Button";
import { useCallback, useEffect, useState } from "react";

/** Блок рефералки в кабинете: ссылка, статистика, один раз свой slug. */
export function ReferralProgramCard() {
  const [data, setData] = useState<ReferralSummary | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [slug, setSlug] = useState("");
  const [loading, setLoading] = useState(false);
  const [savingSlug, setSavingSlug] = useState(false);

  const load = useCallback(() => {
    setLoading(true);
    setErr(null);
    fetchReferralSummary()
      .then(setData)
      .catch((e) =>
        setErr(e instanceof Error ? e.message : "Не удалось загрузить рефералку")
      )
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const fullLink =
    typeof window !== "undefined" && data
      ? `${window.location.origin}/${data.referral_link_query}`
      : "";

  async function copyLink() {
    if (!fullLink || !navigator.clipboard) return;
    try {
      await navigator.clipboard.writeText(fullLink);
    } catch {
      setErr("Не удалось скопировать — выполните копирование вручную.");
    }
  }

  async function saveSlug() {
    if (!slug.trim() || savingSlug) return;
    setSavingSlug(true);
    setErr(null);
    try {
      const next = await updateReferralCode(slug.trim().toLowerCase());
      setData(next);
      setSlug("");
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Не удалось сохранить код");
    } finally {
      setSavingSlug(false);
    }
  }

  if (loading && !data) {
    return (
      <div className="mt-6 rounded-2xl border border-violet-500/20 bg-violet-500/5 px-5 py-5 text-zinc-400">
        Рефералка загружается…
      </div>
    );
  }

  if (!data) {
    return err ? (
      <p className="mt-6 text-sm text-red-400">{err}</p>
    ) : null;
  }

  return (
    <div className="mt-6 rounded-2xl border border-violet-500/25 bg-violet-500/[0.07] px-5 py-5">
      <p className="text-sm font-medium text-violet-200/95">Реферальная программа</p>
      <p className="mt-1 text-sm text-zinc-500">
        С первого пополнения приглашённого начисляется{" "}
        <span className="text-zinc-300">50%</span> от суммы (один раз с каждого). Далее —{" "}
        <span className="text-zinc-300">15%</span> с каждого пополнения.
      </p>
      <p className="mt-3 break-all font-mono text-sm text-zinc-200">{fullLink}</p>
      <div className="mt-3 flex flex-wrap gap-2">
        <Button type="button" variant="outline" onClick={() => void copyLink()}>
          Скопировать ссылку
        </Button>
        <Button type="button" variant="ghost" onClick={() => load()}>
          Обновить
        </Button>
      </div>
      <p className="mt-4 text-sm text-zinc-500">
        Приглашено:{" "}
        <span className="text-zinc-200">{data.referrals_count}</span> · Заработано с
        рефералов:{" "}
        <span className="text-emerald-200/90">
          {(data.rewards_total_cents / 100).toLocaleString("ru-RU")} ₽
        </span>
      </p>
      {!data.slug_locked && (
        <div className="mt-4 border-t border-white/10 pt-4">
          <p className="text-sm text-zinc-500">
            Один раз задаётся код в ссылке (латиница, цифры, дефис; 4–32 символа).
          </p>
          <div className="mt-2 flex flex-wrap items-end gap-2">
            <label className="text-base text-zinc-400">
              Новый код
              <input
                className="mt-1 block w-56 rounded-xl border border-white/10 bg-ink-900/80 px-4 py-2.5 font-mono text-base text-white outline-none focus:ring-2 focus:ring-violet-500/30"
                value={slug}
                onChange={(e) => setSlug(e.target.value)}
                placeholder={data.referral_code}
                maxLength={32}
              />
            </label>
            <Button
              type="button"
              disabled={savingSlug || !slug.trim()}
              onClick={() => void saveSlug()}
            >
              {savingSlug ? "…" : "Зафиксировать"}
            </Button>
          </div>
        </div>
      )}
      {data.slug_locked && (
        <p className="mt-3 text-xs text-zinc-600">
          Код в ссылке зафиксирован. Текущий код:{" "}
          <span className="font-mono text-zinc-400">{data.referral_code}</span>
        </p>
      )}
      {err && <p className="mt-3 text-sm text-red-400">{err}</p>}
    </div>
  );
}
