"use client";

import { Button } from "@/components/ui/Button";
import { GradientHeading } from "@/components/ui/GradientHeading";
import { FreeWordsButtonLabel } from "@/components/ui/SparklesPngIcon";
import { demoRewrite } from "@/api/endpoints";
import { cardLift, springSoft, staggerContainer } from "@/lib/motion";
import { cn } from "@/lib/cn";
import { motion, AnimatePresence } from "framer-motion";
import { useCallback, useEffect, useId, useState } from "react";
import type { BrandVoiceId } from "@/types";
import { VoiceCharacterArt } from "@/components/marketing/VoiceCharacterArt";

/** Порядок на сайте: Aggressive → Expert → Friendly (id совпадают с API). */
const VOICES: {
  id: BrandVoiceId;
  name: string;
  toneLine: string;
  sample: string;
}[] = [
  {
    id: "bold_daring",
    name: "Aggressive",
    toneLine: "Дерзкий, быстрый, с характером",
    sample:
      "Зашёл, глянул, быстро всё понял. Если начинается муть или лишние движения, сразу мимо. Имхо, норм площадки не прячутся и не тянут время.",
  },
  {
    id: "expert_precise",
    name: "Expert",
    toneLine: "Чётко, по фактам, без эмоций",
    sample:
      "При оценке в первую очередь учитываются лицензия и условия вывода. Эти параметры напрямую влияют на надёжность и итоговую стабильность.",
  },
  {
    id: "friendly_warm",
    name: "Friendly",
    toneLine: "Просто и по-человечески",
    sample:
      "Если честно, лучше сначала немного посмотреть и не спешить. Когда всё понятно и спокойно, тогда уже можно нормально зайти и попробовать.",
  },
];

const PLACEHOLDER =
  "Вставь сюда свой черновик (примерно до 50 слов): про казино, бонусы, вывод, лицензию…";

export function DemoSection() {
  const modalId = useId();
  const [openVoice, setOpenVoice] = useState<BrandVoiceId | null>(null);
  const [draft, setDraft] = useState("");
  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const close = useCallback(() => {
    setOpenVoice(null);
    setErr(null);
    setLoading(false);
  }, []);

  useEffect(() => {
    if (!openVoice) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") close();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [openVoice, close]);

  async function applyStyle() {
    if (!openVoice) return;
    const t = draft.trim();
    if (t.length < 10) {
      setErr("Минимум ~10 символов, чтобы смысл было что переписывать.");
      return;
    }
    setErr(null);
    setLoading(true);
    setResult(null);
    try {
      const { result: text } = await demoRewrite({ text: t, voice_id: openVoice });
      setResult(text);
    } catch (e) {
      setErr(
        e instanceof Error ? e.message : "Не удалось связаться с API. Запущен бэкенд?"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="relative z-10 px-4 py-24 md:py-28">
      <div className="relative mx-auto max-w-6xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.35, ease: [0.4, 0, 0.2, 1] }}
          className="text-center"
        >
          <p className="mb-4 inline-flex rounded-full border border-gem-bright/25 bg-emerald-950/50 px-5 py-2 text-sm font-medium tracking-wide text-gem-mist backdrop-blur-md">
            Hero · Стиль текста
          </p>
          <GradientHeading as="h2" className="text-4xl sm:text-5xl md:text-6xl">
            Выбери стиль подачи
          </GradientHeading>
          <p className="mx-auto mt-6 max-w-3xl text-base leading-relaxed text-zinc-400 md:text-lg">
            Три блока — <span className="text-zinc-300">Aggressive</span>,{" "}
            <span className="text-zinc-300">Expert</span>,{" "}
            <span className="text-zinc-300">Friendly</span>. Вставь черновик и нажми
            «Применить стиль» — модель переложит текст в выбранный голос (нужен бэкенд и
            ключ Anthropic).
          </p>
        </motion.div>

        <motion.div
          className="mt-16 grid gap-8 lg:grid-cols-3"
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-80px" }}
        >
          {VOICES.map((v) => (
            <motion.div key={v.id} variants={cardLift} className="group relative h-full">
              <div
                className={cn(
                  "liquid-glass liquid-glass-hover flex h-full flex-col p-8 md:p-9",
                  "before:pointer-events-none before:absolute before:inset-0 before:rounded-3xl before:opacity-0 before:transition-opacity before:duration-500",
                  "group-hover:before:opacity-100 before:bg-[radial-gradient(120%_80%_at_50%_-20%,rgba(52,211,153,0.12),transparent)]"
                )}
              >
                <div className="pointer-events-none absolute inset-0 overflow-hidden rounded-3xl">
                  <div className="absolute inset-0 -translate-x-full skew-x-[-12deg] bg-gradient-to-r from-transparent via-white/[0.07] to-transparent opacity-0 transition-all duration-700 group-hover:translate-x-full group-hover:opacity-100" />
                </div>

                <div className="relative">
                  <VoiceCharacterArt voiceId={v.id} />
                  <h3 className="mt-5 text-center text-2xl font-semibold tracking-tight text-white md:text-3xl">
                    {v.name}
                  </h3>
                  <p className="mt-3 text-center text-sm leading-snug text-zinc-500 md:text-base">
                    {v.toneLine}
                  </p>
                  <figure className="mt-5 rounded-2xl border border-white/[0.08] bg-black/25 px-4 py-4 text-left">
                    <figcaption className="mb-2 text-xs font-medium uppercase tracking-wider text-gem-bright/70">
                      Пример
                    </figcaption>
                    <blockquote className="whitespace-pre-line text-sm leading-relaxed text-zinc-400 md:text-base">
                      {v.sample}
                    </blockquote>
                  </figure>
                </div>

                <div className="relative mt-8 flex flex-1 flex-col justify-end">
                  <Button
                    type="button"
                    variant="outline"
                    className="w-full !border-gem-bright/30 !py-3.5 text-gem-mist hover:!border-gem-bright/60 hover:!shadow-emerald-glow"
                    onClick={() => {
                      setOpenVoice(v.id);
                      setResult(null);
                      setErr(null);
                    }}
                  >
                    <FreeWordsButtonLabel />
                  </Button>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>

      <AnimatePresence>
        {openVoice && (
          <motion.div
            role="dialog"
            aria-modal
            aria-labelledby={modalId}
            className="fixed inset-0 z-[100] flex items-center justify-center p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.22 }}
          >
            <button
              type="button"
              className="absolute inset-0 bg-black/55 backdrop-blur-[20px]"
              aria-label="Закрыть"
              onClick={close}
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.94, y: 12 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.96, y: 8 }}
              transition={springSoft}
              className="relative z-[101] w-full max-w-xl overflow-hidden rounded-3xl border border-gem-bright/20 bg-pitch-soft/90 p-8 shadow-emerald-glow backdrop-blur-2xl md:p-10"
              onClick={(e) => e.stopPropagation()}
              onKeyDown={(e) => e.stopPropagation()}
            >
              <button
                type="button"
                onClick={close}
                className="absolute right-4 top-4 flex h-9 w-9 items-center justify-center rounded-lg border border-white/10 text-zinc-400 transition-colors hover:border-gem-bright/40 hover:text-white"
                aria-label="Закрыть окно"
              >
                ✕
              </button>
              <p id={modalId} className="pr-12 text-2xl font-semibold text-white md:text-3xl">
                Переписать в стиле{" "}
                <span className="text-gem-bright">
                  {VOICES.find((x) => x.id === openVoice)?.name}
                </span>
              </p>
              <p className="mt-2 text-sm text-zinc-500 md:text-base">
                Вставь текст — модель сохранит смысл и переложит в выбранный голос.
              </p>
              <textarea
                className="mt-5 min-h-[160px] w-full resize-y rounded-2xl border border-white/10 bg-black/50 px-5 py-4 text-base leading-relaxed text-zinc-200 outline-none ring-emerald-500/30 placeholder:text-zinc-600 focus:ring-2"
                placeholder={PLACEHOLDER}
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
              />
              {err && (
                <p className="mt-2 text-xs text-red-400">{err}</p>
              )}
              <div className="mt-4 flex flex-wrap gap-2">
                <Button type="button" onClick={applyStyle} disabled={loading}>
                  {loading ? "Переписываю…" : "Применить стиль"}
                </Button>
                <Button type="button" variant="ghost" onClick={close}>
                  Отмена
                </Button>
              </div>
              {result && (
                <motion.div
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-6 rounded-2xl border border-gem-bright/25 bg-black/40 p-5 text-left text-base leading-relaxed text-zinc-200 md:text-lg"
                >
                  {result}
                </motion.div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  );
}
