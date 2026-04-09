"use client";

import {
  HeroWreathDecor,
  HeroWreathMobileCtaColumn,
} from "@/components/marketing/HeroWreathDecor";
import { Button } from "@/components/ui/Button";
import { GradientHeading } from "@/components/ui/GradientHeading";
import { getToken } from "@/lib/auth-storage";
import { motion } from "framer-motion";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

/** Только opacity: без translate/scale у контента — иначе после скролла всплывает шов с overflow и fixed mesh */
const heroEnter = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { duration: 0.32, ease: [0.4, 0, 0.2, 1] },
  },
};

export function Hero() {
  const path = usePathname();
  const [authed, setAuthed] = useState(false);

  useEffect(() => {
    setAuthed(!!getToken());
  }, [path]);

  return (
    <section className="relative overflow-x-hidden px-4 pb-24 pt-28 sm:pb-28 sm:pt-36">
      {/*
        Сплошная база на всю секцию: под ней не виден fixed MeshBackground,
        значит нет стыка с анимированными blur/scale слоями при repaint после скролла.
      */}
      <div
        className="pointer-events-none absolute inset-0 z-0 bg-[#05020D]"
        aria-hidden
      />
      <div
        className="pointer-events-none absolute inset-0 z-0"
        aria-hidden
        style={{
          background:
            "radial-gradient(ellipse 85% 50% at 50% 0%, rgba(88, 28, 135, 0.22), transparent 62%)",
        }}
      />
      <HeroWreathDecor />
      <div className="relative z-10 mx-auto max-w-5xl text-center">
        <motion.div
          variants={heroEnter}
          initial="hidden"
          animate="visible"
          className="mx-auto flex max-w-4xl flex-col items-center"
        >
          <p className="mb-6 inline-flex rounded-full border border-white/10 bg-white/[0.08] px-6 py-2.5 text-sm font-medium uppercase tracking-[0.16em] text-violet-200/90 sm:text-base">
            SaaS для PBN · AI-конвейер
          </p>
          <ul
            className="mb-10 flex flex-wrap items-center justify-center gap-x-5 gap-y-2 text-base font-medium text-zinc-400 sm:text-lg"
            aria-label="Ценности продукта"
          >
            <li className="text-violet-200/95">Высокотехнологичность</li>
            <li className="hidden text-zinc-600 sm:inline" aria-hidden>
              ·
            </li>
            <li className="text-indigo-200/90">Premium</li>
            <li className="hidden text-zinc-600 sm:inline" aria-hidden>
              ·
            </li>
            <li className="text-emerald-300/90">Совершенство</li>
          </ul>
          <GradientHeading
            as="h1"
            className="text-5xl font-bold leading-[1.08] tracking-[-0.03em] sm:text-6xl md:text-7xl"
          >
            Завод SEO-статей под казино
          </GradientHeading>
          <p className="mt-12 max-w-3xl text-xl leading-relaxed text-slate-400 sm:text-2xl">
            Бренд, ключи, LSI, голос подачи — на выходе структурированный текст и{" "}
            <span className="text-violet-200/90">.docx</span> на почту. Без ручной возни
            с копирайтерами.
          </p>
          <div className="mt-16 w-full">
            <div className="flex flex-col items-center gap-4 lg:hidden">
              {/* Полная ширина экрана: столбики у краёв, кнопка по центру */}
              <div className="relative left-1/2 w-screen max-w-[100vw] -translate-x-1/2 px-4">
                {/*
                  Симметрия: одинаковая ширина слотов под столбики + два равных 1fr до CTA —
                  иначе auto-колонки разной ширины дают разный визуальный зазор до кнопки.
                */}
                <div className="grid w-full grid-cols-[4.5rem_minmax(0,1fr)_auto_minmax(0,1fr)_4.5rem] items-center sm:grid-cols-[5rem_minmax(0,1fr)_auto_minmax(0,1fr)_5rem]">
                  <div className="flex min-w-0 justify-end">
                    <HeroWreathMobileCtaColumn side="left" />
                  </div>
                  <div className="min-w-0" aria-hidden />
                  <div className="flex shrink-0 justify-center">
                    {authed ? (
                      <Button
                        href="/dashboard"
                        primaryCta
                        className="min-w-0 px-5 sm:px-7"
                      >
                        В кабинет
                      </Button>
                    ) : (
                      <Button
                        href="/register"
                        primaryCta
                        className="min-w-0 px-5 sm:px-7"
                      >
                        Старт — регистрация
                      </Button>
                    )}
                  </div>
                  <div className="min-w-0" aria-hidden />
                  <div className="flex min-w-0 justify-start">
                    <HeroWreathMobileCtaColumn side="right" />
                  </div>
                </div>
              </div>
              <Button variant="ghost" href="/guide">
                Как это работает
              </Button>
            </div>
            <div className="hidden flex-wrap items-center justify-center gap-6 lg:flex">
              {authed ? (
                <>
                  <Button href="/dashboard" primaryCta>
                    Кабинет
                  </Button>
                  <Button variant="outline" href="/order">
                    Новый заказ
                  </Button>
                </>
              ) : (
                <Button href="/register" primaryCta>
                  Старт — регистрация
                </Button>
              )}
              <Button variant="ghost" href="/guide">
                Как это работает
              </Button>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
