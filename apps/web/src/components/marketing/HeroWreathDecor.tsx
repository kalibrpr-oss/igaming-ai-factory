"use client";

import { cn } from "@/lib/cn";
import Image from "next/image";

/**
 * Декоративный «венок» из 6 PNG вокруг hero-контента.
 * Файлы: `public/hero-wreath/{bank,safe,money-bag,pyramid,cash-register,piggy-bank}.png`
 */
type WreathSide = "left" | "right";

type WreathItem = {
  src: string;
  /** Бокс отображения (px), разные — для живой композиции */
  size: number;
  top: string;
  side: WreathSide;
  /** Отступ от края секции */
  edge: string;
  rotateDeg: number;
  opacity: number;
};

const WREATH_ITEMS: WreathItem[] = [
  /* Слева сверху → вниз: дальше — ближе к центру — снова дальше */
  {
    src: "/hero-wreath/bank.png",
    size: 88,
    top: "12%",
    side: "left",
    edge: "1.5%",
    rotateDeg: -10,
    opacity: 0.46,
  },
  {
    src: "/hero-wreath/safe.png",
    size: 108,
    top: "46%",
    side: "left",
    edge: "5.5%",
    rotateDeg: 4,
    opacity: 0.5,
  },
  {
    src: "/hero-wreath/money-bag.png",
    size: 84,
    top: "78%",
    side: "left",
    edge: "2.8%",
    rotateDeg: -7,
    opacity: 0.44,
  },
  /* Справа: зеркально по логике дуги */
  {
    src: "/hero-wreath/pyramid.png",
    size: 94,
    top: "12%",
    side: "right",
    edge: "1.5%",
    rotateDeg: 11,
    opacity: 0.46,
  },
  {
    src: "/hero-wreath/cash-register.png",
    size: 104,
    top: "46%",
    side: "right",
    edge: "5.5%",
    rotateDeg: -5,
    opacity: 0.5,
  },
  {
    src: "/hero-wreath/piggy-bank.png",
    size: 82,
    top: "78%",
    side: "right",
    edge: "2.8%",
    rotateDeg: 8,
    opacity: 0.44,
  },
];

const imageFilter =
  "[filter:drop-shadow(0_6px_18px_rgba(0,0,0,0.42))_drop-shadow(0_0_22px_rgba(139,92,246,0.14))]";

/** Лёгкая тень для мелких иконок на мобилке */
const imageFilterMobile =
  "[filter:drop-shadow(0_3px_10px_rgba(0,0,0,0.38))_drop-shadow(0_0_14px_rgba(139,92,246,0.12))]";

/**
 * Дуга как дуга «)» к кнопке: верх/низ ближе к «позвоночнику», середина — выступ к центру.
 * Парабола по Y: dx ~ (1 - (y/ymax)²), симметрично слева/справа.
 */
const CTA_ARC_DY = [-13, 0, 13] as const;
const CTA_ARC_DX_PEAK = 22;
const CTA_ARC_DX_END = 5;

function ctaArcDxLeft(i: number): number {
  const y = CTA_ARC_DY[i] ?? 0;
  const ymax = 13;
  const t = 1 - (y / ymax) * (y / ymax);
  return CTA_ARC_DX_END + (CTA_ARC_DX_PEAK - CTA_ARC_DX_END) * t;
}

function ctaArcDxRight(i: number): number {
  return -ctaArcDxLeft(i);
}

type CtaColumnSide = "left" | "right";

/**
 * Вертикальный столбик из 3 PNG по бокам кнопки «Старт — регистрация» (только до breakpoint lg).
 */
export function HeroWreathMobileCtaColumn({ side }: { side: CtaColumnSide }) {
  const items = WREATH_ITEMS.filter((x) => x.side === side);
  return (
    <div
      className={cn(
        "pointer-events-none flex shrink-0 flex-col justify-center gap-y-1 py-1",
        side === "left" ? "items-end" : "items-start"
      )}
      aria-hidden
    >
      {items.map((item, i) => {
        const sidePx = Math.round(item.size * 0.5);
        const dx =
          side === "left" ? ctaArcDxLeft(i) : ctaArcDxRight(i);
        const dy = CTA_ARC_DY[i] ?? 0;
        const rot = item.rotateDeg * 0.52 + (side === "left" ? [-4, 0, 3][i] ?? 0 : [4, 0, -3][i] ?? 0);
        return (
          <div
            key={item.src}
            className="shrink-0"
            style={{
              width: sidePx,
              height: sidePx,
              opacity: Math.min(0.56, item.opacity + 0.06),
              transform: `translate(${dx}px, ${dy}px) rotate(${rot}deg)`,
            }}
          >
            <Image
              src={item.src}
              alt=""
              width={512}
              height={512}
              sizes={`${sidePx}px`}
              className={cn(
                "h-full w-full select-none object-contain object-center",
                imageFilterMobile
              )}
            />
          </div>
        );
      })}
    </div>
  );
}

export function HeroWreathDecor() {
  return (
    <div
      className={cn(
        "pointer-events-none absolute inset-0 z-[1]",
        "hidden lg:block"
      )}
      aria-hidden
    >
      <div className="relative h-full w-full origin-top scale-[0.88] xl:scale-100">
        {WREATH_ITEMS.map((item) => (
          <div
            key={item.src}
            className="absolute"
            style={{
              top: item.top,
              ...(item.side === "left"
                ? { left: item.edge }
                : { right: item.edge }),
              width: item.size,
              height: item.size,
              opacity: item.opacity,
              transform: `translateY(-50%) rotate(${item.rotateDeg}deg)`,
            }}
          >
            <Image
              src={item.src}
              alt=""
              width={512}
              height={512}
              sizes="(min-width: 1280px) 120px, 100px"
              className={cn(
                "h-full w-full select-none object-contain object-center",
                imageFilter
              )}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
