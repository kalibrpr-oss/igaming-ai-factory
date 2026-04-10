"use client";

import { Button } from "@/components/ui/Button";
import { GradientHeading } from "@/components/ui/GradientHeading";
import { FreeWordsButtonLabel } from "@/components/ui/SparklesPngIcon";
import { demoRewrite } from "@/api/endpoints";
import { cn } from "@/lib/cn";
import { springSoft } from "@/lib/motion";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import Image from "next/image";
import {
  useCallback,
  useEffect,
  useId,
  useState,
} from "react";
import type { BrandVoiceId } from "@/types";
import { VoiceCharacterArt } from "@/components/marketing/VoiceCharacterArt";

const PLACEHOLDER =
  "Черновик до ~50 слов (например: казино, бонусы, вывод; или тема из вашей ниши).";

type RowLayout = "image-left" | "image-right";

const ROWS: {
  id: BrandVoiceId;
  name: string;
  toneLine: string;
  sample: string;
  layout: RowLayout;
  accent: "emerald" | "cyan" | "violet";
}[] = [
  {
    id: "bold_daring",
    name: "Aggressive",
    toneLine: "Прямо, быстро, с акцентом",
    sample:
      "Оценка занимает мало времени: интерфейс и условия читаются без лишних шагов. Площадки уровня не скрывают ключевые параметры и не затягивают ответы.",
    layout: "image-left",
    accent: "emerald",
  },
  {
    id: "expert_precise",
    name: "Expert",
    toneLine: "Чётко, по фактам, без эмоций",
    sample:
      "При оценке в первую очередь учитываются лицензия и условия вывода. Эти параметры напрямую влияют на надёжность и итоговую стабильность.",
    layout: "image-right",
    accent: "cyan",
  },
  {
    id: "friendly_warm",
    name: "Friendly",
    toneLine: "Спокойно, понятно, без перегруза",
    sample:
      "Имеет смысл сначала изучить интерфейс и условия без спешки. Когда структура ясна, можно переходить к регистрации и тестовому депозиту.",
    layout: "image-left",
    accent: "violet",
  },
];

/** Мягкое свечение вокруг PNG без рамки и без «коробки» */
const characterAura: Record<
  (typeof ROWS)[number]["accent"],
  string
> = {
  emerald:
    "0 28px 56px -18px rgba(0,0,0,0.5), 0 0 72px -20px rgba(52, 211, 153, 0.28)",
  cyan:
    "0 28px 56px -18px rgba(0,0,0,0.5), 0 0 72px -20px rgba(56, 189, 248, 0.26)",
  violet:
    "0 28px 56px -18px rgba(0,0,0,0.5), 0 0 72px -20px rgba(167, 139, 250, 0.26)",
};

/** PNG с прозрачным фоном в `public/brand-voice/` — иначе fallback: `VoiceCharacterArt` */
const BRAND_VOICE_PNG: Partial<
  Record<BrandVoiceId, { src: string; alt: string }>
> = {
  bold_daring: { src: "/brand-voice/aggressive.png", alt: "Aggressive" },
  expert_precise: { src: "/brand-voice/expert.png", alt: "Expert" },
  friendly_warm: { src: "/brand-voice/friendly.png", alt: "Friendly" },
};

export function BrandVoicesSectionPremium() {
  const modalId = useId();
  const reduceMotion = useReducedMotion();
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
        e instanceof Error ? e.message : "Нет ответа API. Проверьте сеть и доступность бэкенда."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <section
      id="demo-brand-voices"
      className="relative z-10 scroll-mt-24 overflow-hidden border-t border-white/[0.04] px-4 py-20 md:py-28"
    >
      <div className="relative mx-auto max-w-6xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.35, ease: [0.4, 0, 0.2, 1] }}
          className="text-center"
        >
          <p className="mb-4 inline-flex rounded-full border border-gem-bright/25 bg-emerald-950/40 px-5 py-2 text-sm font-medium tracking-wide text-gem-mist backdrop-blur-md">
            Стиль текста
          </p>
          <GradientHeading as="h2" className="text-4xl sm:text-5xl md:text-6xl">
            Три стиля подачи
          </GradientHeading>
          <p className="mx-auto mt-6 max-w-2xl text-base leading-relaxed text-zinc-400 md:text-lg">
            Три стиля подачи в одном продукте. Выберите линию и проверьте на своём черновике.
          </p>
        </motion.div>

        <div className="mt-16 flex flex-col gap-10 md:gap-14 lg:gap-16">
          {ROWS.map((row, i) => {
            const pngArt = BRAND_VOICE_PNG[row.id];
            return (
            <motion.article
              key={row.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{
                duration: 0.38,
                delay: i * 0.06,
                ease: [0.4, 0, 0.2, 1],
              }}
              whileHover={
                reduceMotion
                  ? undefined
                  : {
                      scale: 1.02,
                      transition: { duration: 0.28, ease: [0.4, 0, 0.2, 1] },
                    }
              }
              className={cn(
                "group relative flex origin-center flex-col gap-8 rounded-[22px] border border-white/[0.08] bg-gradient-to-br from-white/[0.05] to-transparent p-8 backdrop-blur-xl will-change-transform md:gap-12 md:rounded-[26px] md:p-10 lg:gap-14 lg:p-12 xl:p-14",
                row.layout === "image-right"
                  ? "lg:flex-row-reverse lg:items-center"
                  : "lg:flex-row lg:items-center"
              )}
              style={{
                boxShadow:
                  "inset 0 1px 0 0 rgba(255,255,255,0.06), 0 24px 80px -40px rgba(0,0,0,0.65)",
              }}
            >
              <div
                className={cn(
                  "flex w-full shrink-0 justify-center lg:w-[min(100%,360px)]",
                  row.layout === "image-right" ? "lg:justify-end" : "lg:justify-start"
                )}
              >
                <motion.div
                  className="relative flex w-full max-w-[360px] justify-center"
                  animate={
                    reduceMotion
                      ? undefined
                      : { y: [0, -6, 0] }
                  }
                  transition={
                    reduceMotion
                      ? undefined
                      : { duration: 5.5, repeat: Infinity, ease: "easeInOut" }
                  }
                >
                  {pngArt ? (
                    <Image
                      src={pngArt.src}
                      alt={pngArt.alt}
                      width={360}
                      height={480}
                      sizes="360px"
                      className="h-auto w-[min(100%,360px)] max-w-[360px] object-contain"
                      style={{ filter: "drop-shadow(0 18px 36px rgba(0,0,0,0.42))" }}
                      draggable={false}
                    />
                  ) : (
                    <div
                      className="overflow-hidden rounded-[22px]"
                      style={{ boxShadow: characterAura[row.accent] }}
                    >
                      <VoiceCharacterArt
                        voiceId={row.id}
                        className="!mx-0 h-[280px] w-full max-w-[360px] rounded-none md:h-[300px] lg:h-[320px]"
                      />
                    </div>
                  )}
                  {pngArt ? (
                    <span
                      className="pointer-events-none absolute inset-0 -z-10 rounded-full opacity-90 blur-3xl"
                      style={{
                        background:
                          row.accent === "emerald"
                            ? "radial-gradient(closest-side, rgba(52,211,153,0.18), transparent 70%)"
                            : row.accent === "cyan"
                              ? "radial-gradient(closest-side, rgba(56,189,248,0.16), transparent 70%)"
                              : "radial-gradient(closest-side, rgba(167,139,250,0.16), transparent 70%)",
                      }}
                      aria-hidden
                    />
                  ) : null}
                </motion.div>
              </div>

              <div className="min-w-0 flex-1 text-center lg:text-left">
                <h3 className="text-[1.75rem] font-semibold leading-tight tracking-tight text-white md:text-[2rem] lg:text-[2.125rem]">
                  {row.name}
                </h3>
                <p className="mt-2 text-sm text-zinc-400 opacity-70 md:text-base">
                  {row.toneLine}
                </p>
                <p className="mx-auto mt-6 max-w-[600px] text-left text-base leading-[1.6] text-zinc-300 md:text-lg lg:mx-0">
                  {row.sample}
                </p>
                <div className="mt-8 flex flex-wrap justify-center gap-3 lg:justify-start">
                  <Button
                    type="button"
                    variant="outline"
                    className="!border-gem-bright/35 !py-3 text-gem-mist hover:!border-gem-bright/55 hover:!shadow-emerald-glow"
                    onClick={() => {
                      setOpenVoice(row.id);
                      setResult(null);
                      setErr(null);
                    }}
                  >
                    <FreeWordsButtonLabel />
                  </Button>
                </div>
              </div>
            </motion.article>
            );
          })}
        </div>
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
                  {ROWS.find((x) => x.id === openVoice)?.name}
                </span>
              </p>
              <p className="mt-2 text-sm text-zinc-500 md:text-base">
                Текст сохраняет смысл; стиль приводится к выбранному голосу.
              </p>
              <textarea
                className="mt-5 min-h-[160px] w-full resize-y rounded-2xl border border-white/10 bg-black/50 px-5 py-4 text-base leading-relaxed text-zinc-200 outline-none ring-emerald-500/30 placeholder:text-zinc-600 focus:ring-2"
                placeholder={PLACEHOLDER}
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
              />
              {err && <p className="mt-2 text-xs text-red-400">{err}</p>}
              <div className="mt-4 flex flex-wrap gap-2">
                <Button type="button" onClick={applyStyle} disabled={loading}>
                  {loading ? "Обработка…" : "Применить стиль"}
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
