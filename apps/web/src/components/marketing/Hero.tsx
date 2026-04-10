"use client";

import { HeroWreathDecor } from "@/components/marketing/HeroWreathDecor";
import { Button } from "@/components/ui/Button";
import { GradientHeading } from "@/components/ui/GradientHeading";
import { motion } from "framer-motion";

/** Только opacity: без translate/scale у контента — иначе после скролла всплывает шов с overflow и fixed mesh */
const heroEnter = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { duration: 0.32, ease: [0.4, 0, 0.2, 1] },
  },
};

export function Hero() {
  return (
    <section className="relative overflow-x-hidden px-4 pb-24 pt-14 sm:pb-28 sm:pt-16 md:pt-[4.5rem]">
      {/*
        Сплошная база на всю секцию: под ней не виден fixed MeshBackground,
        значит нет стыка с анимированными blur/scale слоями при repaint после скролла.
      */}
      <div
        className="pointer-events-none absolute inset-0 z-0 bg-[#05020D]"
        aria-hidden
      />
      <HeroWreathDecor />
      {/*
        Крупная светлая дуга за типографикой (референс Quantix): мягкий эллипс снизу слоя + лёгкий «обод».
      */}
      <div
        className="pointer-events-none absolute left-1/2 top-[4.5rem] z-[2] h-[min(28rem,78vw)] w-[min(110rem,220vw)] -translate-x-1/2 blur-[48px] sm:top-[5.5rem] md:top-[6.5rem] md:h-[min(32rem,85vw)] md:blur-[56px]"
        style={{
          background:
            "radial-gradient(ellipse 100% 48% at 50% 100%, rgba(255,255,255,0.2) 0%, rgba(233,213,255,0.14) 18%, rgba(167,139,250,0.1) 36%, rgba(99,102,241,0.06) 52%, transparent 68%)",
        }}
        aria-hidden
      />
      <div
        className="pointer-events-none absolute left-1/2 top-[5rem] z-[2] h-[min(14rem,42vw)] w-[min(72rem,160vw)] -translate-x-1/2 blur-[20px] sm:top-[6rem] md:top-[7rem] md:blur-[24px]"
        style={{
          background:
            "radial-gradient(ellipse 95% 38% at 50% 100%, rgba(255,255,255,0.28) 0%, rgba(244,240,255,0.12) 35%, transparent 58%)",
        }}
        aria-hidden
      />
      <div className="relative z-10 mx-auto max-w-5xl text-center">
        <motion.div
          variants={heroEnter}
          initial="hidden"
          animate="visible"
          className="mx-auto flex max-w-4xl flex-col items-center"
        >
          <p className="mb-5 text-center sm:mb-6" aria-label="Conveer 2.0">
            <span className="inline-flex flex-wrap items-baseline justify-center text-3xl font-semibold leading-none tracking-[-0.04em] [font-feature-settings:normal] [font-variant-numeric:normal] sm:text-4xl md:text-[2.35rem]">
              <span className="heading-shimmer text-transparent">Conveer</span>
              <span className="heading-shimmer ml-[0.22em] text-[0.87em] text-transparent">
                2.0
              </span>
            </span>
          </p>
          <p className="mb-6 inline-flex rounded-full border border-white/10 bg-white/[0.08] px-6 py-2.5 text-sm font-medium uppercase tracking-[0.16em] text-violet-200/90 sm:text-base">
            SaaS · PBN · тематика в параметрах заказа
          </p>
          <GradientHeading
            as="h1"
            className="text-[2.65rem] font-bold leading-[1.08] tracking-[-0.03em] sm:text-5xl md:text-6xl"
          >
            SEO-статьи: iGaming и другие ниши
          </GradientHeading>
          <p className="mt-12 max-w-3xl text-xl leading-relaxed text-slate-400 sm:text-2xl">
            В форме — бренд, ключи, LSI, стиль подачи. На выходе — структура и{" "}
            <span className="text-violet-200/90">.docx</span> на почту. Тематика задаётся
            параметрами заказа; типовой профиль — iGaming и PBN.
          </p>
          <div className="mt-14 flex w-full flex-row flex-wrap items-center justify-center gap-4 sm:mt-16 sm:gap-5">
            <Button href="/order" primaryCta className="min-w-[10.5rem]">
              Новый заказ
            </Button>
            <Button variant="ghost" href="/guide" className="min-w-[10.5rem]">
              Как это работает
            </Button>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
