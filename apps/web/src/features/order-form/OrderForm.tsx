"use client";

import { createOrder, fetchBrandVoices, previewOrderPrice } from "@/api/endpoints";
import { Button } from "@/components/ui/Button";
import { buildOrderPayload, type SeoForm } from "@/lib/order-schema";
import { cn } from "@/lib/cn";
import type { BrandVoiceMeta, OrderQuoteResponse } from "@/types";
import { useCallback, useEffect, useState } from "react";

const defaultSeo: SeoForm = {
  language: "ru",
  primary_keyword: "",
  keyword_density_percent: 1.5,
  heading_format: "strict_h1_h2_h3",
  meta_description_length: 160,
  article_type: "review",
  include_faq_block: true,
  include_table_compare: false,
  canonical_url_hint: "",
};

export function OrderForm() {
  const [voices, setVoices] = useState<BrandVoiceMeta[]>([]);
  const [brandName, setBrandName] = useState("");
  const [taskNotes, setTaskNotes] = useState("");
  const [keywordsRaw, setKeywordsRaw] = useState("");
  const [lsiRaw, setLsiRaw] = useState("");
  const [words, setWords] = useState(1500);
  const [voiceId, setVoiceId] = useState("expert_precise");
  const [seo, setSeo] = useState<SeoForm>(defaultSeo);
  const [quote, setQuote] = useState<OrderQuoteResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    fetchBrandVoices()
      .then((r) => {
        setVoices(r.items);
        if (r.items.length) {
          setVoiceId((cur) =>
            r.items.some((v) => v.id === cur) ? cur : r.items[0].id
          );
        }
      })
      .catch(() => setErr("Не удалось загрузить голоса — проверь API."));
  }, []);

  const refreshQuote = useCallback(async () => {
    try {
      const q = await previewOrderPrice({
        target_word_count: words,
        brand_voice_id: voiceId,
      });
      setQuote(q);
      setErr(null);
    } catch {
      setQuote(null);
    }
  }, [words, voiceId]);

  useEffect(() => {
    const t = window.setTimeout(() => {
      void refreshQuote();
    }, 280);
    return () => window.clearTimeout(t);
  }, [refreshQuote]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setMsg(null);
    setErr(null);
    const built = buildOrderPayload({
      brand_name: brandName,
      task_notes: taskNotes,
      keywords_raw: keywordsRaw,
      lsi_raw: lsiRaw,
      target_word_count: words,
      brand_voice_id: voiceId,
      seo,
    });
    if (!built.ok) {
      setErr(built.error);
      return;
    }
    setLoading(true);
    try {
      const order = await createOrder(built.payload);
      setMsg(`Заказ #${order.id} создан. Статус: ${order.status} — дальше подключим оплату.`);
    } catch (er) {
      setErr(er instanceof Error ? er.message : "Ошибка создания заказа");
    } finally {
      setLoading(false);
    }
  }

  function updateSeo<K extends keyof SeoForm>(key: K, v: SeoForm[K]) {
    setSeo((s) => ({ ...s, [key]: v }));
  }

  return (
    <form onSubmit={onSubmit} className="mx-auto max-w-3xl space-y-10 pb-20">
      <div className="glass-panel p-8 sm:p-10">
        <h2 className="text-2xl font-semibold text-white">ТЗ и бренд</h2>
        <div className="mt-6 space-y-5">
          <label className="block text-base text-zinc-400">
            Название бренда / казино
            <input
              className="mt-2 w-full rounded-xl border border-white/10 bg-ink-900/80 px-4 py-3 text-base text-white outline-none ring-emerald-500/40 transition-[box-shadow] duration-[250ms] focus:ring-2"
              value={brandName}
              onChange={(e) => setBrandName(e.target.value)}
              required
            />
          </label>
          <label className="block text-base text-zinc-400">
            Заметки к ТЗ (опционально)
            <textarea
              className="mt-2 min-h-[100px] w-full rounded-xl border border-white/10 bg-ink-900/80 px-4 py-3 text-base text-white outline-none ring-emerald-500/40 transition-[box-shadow] duration-[250ms] focus:ring-2"
              value={taskNotes}
              onChange={(e) => setTaskNotes(e.target.value)}
            />
          </label>
        </div>
      </div>

      <div className="glass-panel p-8 sm:p-10">
        <h2 className="text-2xl font-semibold text-white">Ключи и LSI</h2>
        <p className="mt-2 text-sm text-zinc-500 md:text-base">
          Через запятую или с новой строки. Главный ключ продублируй в SEO-блоке ниже.
        </p>
        <div className="mt-6 space-y-5">
          <label className="block text-base text-zinc-400">
            Ключевые фразы
            <textarea
              className="mt-2 min-h-[120px] w-full rounded-xl border border-white/10 bg-ink-900/80 px-4 py-3 font-mono text-base text-white outline-none ring-emerald-500/40 focus:ring-2"
              value={keywordsRaw}
              onChange={(e) => setKeywordsRaw(e.target.value)}
              placeholder="vodka casino отзывы, вывод на карту"
              required
            />
          </label>
          <label className="block text-base text-zinc-400">
            LSI / семантика
            <textarea
              className="mt-2 min-h-[96px] w-full rounded-xl border border-white/10 bg-ink-900/80 px-4 py-3 font-mono text-base text-white outline-none ring-emerald-500/40 focus:ring-2"
              value={lsiRaw}
              onChange={(e) => setLsiRaw(e.target.value)}
              placeholder="вагер, зеркало, лицензия, слоты"
            />
          </label>
        </div>
      </div>

      <div className="glass-panel p-8 sm:p-10">
        <h2 className="text-2xl font-semibold text-white">Объём и голос</h2>
        <div className="mt-6 grid gap-8 sm:grid-cols-2">
          <label className="block text-base text-zinc-400">
            Целевой объём, слов
            <input
              type="number"
              min={300}
              max={15000}
              className="mt-2 w-full rounded-xl border border-white/10 bg-ink-900/80 px-4 py-3 text-base text-white outline-none ring-emerald-500/40 focus:ring-2"
              value={words}
              onChange={(e) => setWords(Number(e.target.value))}
            />
          </label>
          <div>
            <p className="text-base text-zinc-400">Стиль текста</p>
            <div className="mt-3 flex flex-wrap gap-2.5">
              {voices.map((v) => (
                <button
                  key={v.id}
                  type="button"
                  onClick={() => setVoiceId(v.id)}
                  className={cn(
                    "rounded-xl border px-4 py-3 text-left text-sm transition-all duration-[250ms] ease-smooth",
                    voiceId === v.id
                      ? "border-gem-bright/70 bg-emerald-500/15 text-gem-mist"
                      : "border-white/10 bg-white/[0.03] text-zinc-400 hover:border-gem-bright/25"
                  )}
                >
                  <span className="font-medium">{v.label}</span>
                  <span className="mt-1 block text-xs text-zinc-500">{v.description}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
        {quote && (
          <p className="mt-8 rounded-xl border border-emerald-500/20 bg-emerald-500/10 px-5 py-4 text-base text-emerald-200/90">
            Ориентир цены:{" "}
            <strong>{(quote.price_cents / 100).toLocaleString("ru-RU")} ₽</strong> за{" "}
            {quote.target_word_count} слов ({quote.currency})
          </p>
        )}
      </div>

      <div className="glass-panel p-8 sm:p-10">
        <h2 className="text-2xl font-semibold text-white">SEO-параметры</h2>
        <div className="mt-6 grid gap-5 sm:grid-cols-2">
          <label className="block text-base text-zinc-400">
            Язык (ISO)
            <input
              className="mt-2 w-full rounded-xl border border-white/10 bg-ink-900/80 px-4 py-3 text-base text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
              value={seo.language}
              onChange={(e) => updateSeo("language", e.target.value)}
            />
          </label>
          <label className="block text-base text-zinc-400">
            Главный ключ (плотность/H1)
            <input
              className="mt-2 w-full rounded-xl border border-white/10 bg-ink-900/80 px-4 py-3 text-base text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
              value={seo.primary_keyword}
              onChange={(e) => updateSeo("primary_keyword", e.target.value)}
              required
            />
          </label>
          <label className="block text-base text-zinc-400 sm:col-span-2">
            Плотность ключа, % ({seo.keyword_density_percent})
            <input
              type="range"
              min={0.5}
              max={3}
              step={0.1}
              className="mt-2 w-full accent-emerald-500"
              value={seo.keyword_density_percent}
              onChange={(e) =>
                updateSeo("keyword_density_percent", Number(e.target.value))
              }
            />
          </label>
          <label className="block text-base text-zinc-400">
            Структура заголовков
            <select
              className="mt-2 w-full rounded-xl border border-white/10 bg-ink-900/80 px-4 py-3 text-base text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
              value={seo.heading_format}
              onChange={(e) =>
                updateSeo(
                  "heading_format",
                  e.target.value as SeoForm["heading_format"]
                )
              }
            >
              <option value="strict_h1_h2_h3">H1 → H2 → H3</option>
              <option value="flat_h2_only">Только H2</option>
              <option value="review_blocks">Блоки обзора</option>
            </select>
          </label>
          <label className="block text-base text-zinc-400">
            Meta description, символов ({seo.meta_description_length})
            <input
              type="range"
              min={120}
              max={200}
              className="mt-2 w-full accent-emerald-500"
              value={seo.meta_description_length}
              onChange={(e) =>
                updateSeo("meta_description_length", Number(e.target.value))
              }
            />
          </label>
          <label className="block text-base text-zinc-400 sm:col-span-2">
            Тип статьи
            <select
              className="mt-2 w-full rounded-xl border border-white/10 bg-ink-900/80 px-4 py-3 text-base text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
              value={seo.article_type}
              onChange={(e) =>
                updateSeo("article_type", e.target.value as SeoForm["article_type"])
              }
            >
              <option value="review">Обзор</option>
              <option value="comparison">Сравнение</option>
              <option value="guide">Гайд</option>
              <option value="bonus">Бонусы</option>
              <option value="news">Новости</option>
            </select>
          </label>
          <label className="flex items-center gap-3 text-base text-zinc-300">
            <input
              type="checkbox"
              checked={seo.include_faq_block}
              onChange={(e) => updateSeo("include_faq_block", e.target.checked)}
              className="rounded border-white/20 bg-ink-900 accent-emerald-500"
            />
            Блок FAQ
          </label>
          <label className="flex items-center gap-3 text-base text-zinc-300">
            <input
              type="checkbox"
              checked={seo.include_table_compare}
              onChange={(e) => updateSeo("include_table_compare", e.target.checked)}
              className="rounded border-white/20 bg-ink-900 accent-emerald-500"
            />
            Таблица сравнения
          </label>
          <label className="block text-base text-zinc-400 sm:col-span-2">
            Подсказка canonical URL
            <input
              className="mt-2 w-full rounded-xl border border-white/10 bg-ink-900/80 px-4 py-3 text-base text-white outline-none focus:ring-2 focus:ring-emerald-500/40"
              value={seo.canonical_url_hint ?? ""}
              onChange={(e) => updateSeo("canonical_url_hint", e.target.value)}
              placeholder="https://..."
            />
          </label>
        </div>
      </div>

      {err && (
        <p className="rounded-xl border border-red-500/30 bg-red-500/10 px-5 py-4 text-base text-red-200">
          {err}
        </p>
      )}
      {msg && (
        <p className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-5 py-4 text-base text-emerald-100">
          {msg}
        </p>
      )}

      <Button
        type="submit"
        className="w-full sm:w-auto"
        disabled={loading}
        variant="primary"
      >
        {loading ? "Отправка…" : "Создать заказ"}
      </Button>
    </form>
  );
}
