"use client";

import { motion } from "framer-motion";
import type { CSSProperties } from "react";

/** Неоновые «орбы» — изумруд / циан / индиго (глубина под premium landing). */
const BLOBS: {
  className: string;
  style: CSSProperties;
  animate: Record<string, number[]>;
  transition: {
    duration: number;
    repeat: number;
    ease: "easeInOut";
    delay?: number;
  };
}[] = [
  {
    className: "left-[-18%] top-[8%] h-[min(75vh,640px)] w-[min(80vw,560px)]",
    style: {
      background:
        "radial-gradient(ellipse 70% 60% at 50% 45%, rgba(139, 92, 246, 0.35) 0%, rgba(88, 28, 135, 0.12) 50%, transparent 72%)",
    },
    animate: { x: [0, 36, -14, 0], y: [0, 22, -18, 0], scale: [1, 1.06, 0.98, 1] },
    transition: { duration: 24, repeat: Infinity, ease: "easeInOut" as const },
  },
  {
    className: "right-[-15%] top-[20%] h-[min(70vh,580px)] w-[min(72vw,520px)]",
    style: {
      background:
        "radial-gradient(ellipse 65% 55% at 40% 50%, rgba(52, 211, 153, 0.28) 0%, rgba(16, 185, 129, 0.1) 50%, transparent 70%)",
    },
    animate: { x: [0, -32, 20, 0], y: [0, 28, -24, 0], scale: [1, 1.05, 1.02, 1] },
    transition: {
      duration: 21,
      repeat: Infinity,
      ease: "easeInOut",
      delay: 1,
    },
  },
  {
    className: "left-[5%] bottom-[-10%] h-[min(85vh,700px)] w-[min(88vw,680px)]",
    style: {
      background:
        "radial-gradient(ellipse 75% 60% at 50% 40%, rgba(59, 130, 246, 0.22) 0%, rgba(30, 64, 175, 0.35) 55%, rgba(15, 23, 42, 0.5) 80%, transparent 100%)",
    },
    animate: { x: [0, -24, 28, 0], y: [0, -20, 14, 0], scale: [1, 1.04, 1, 1] },
    transition: {
      duration: 28,
      repeat: Infinity,
      ease: "easeInOut",
      delay: 2,
    },
  },
];

/**
 * Многослойный фон: deep base, hero glow (дыхание), glow arc, mesh, шум.
 * Референс: dark futuristic / Quantix-level глубина — без внешних картинок.
 */
export function MeshBackground() {
  return (
    <div
      className="pointer-events-none fixed inset-0 z-0 overflow-hidden"
      aria-hidden
    >
      {/* База: почти чёрный с фиолетовым дном */}
      <div className="absolute inset-0 bg-[#05020D]" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_120%_80%_at_50%_100%,rgba(15,23,42,0.9),transparent_55%)]" />

      {/* Полуовал сверху: статичный blur без keyframes — иначе при repaint после скролла граница слоя заметна у hero */}
      <div
        className="absolute left-1/2 top-[-18%] h-[min(58vh,520px)] w-[min(135vw,1100px)] -translate-x-1/2 rounded-[50%] opacity-[0.72]"
        style={{
          background:
            "radial-gradient(ellipse 100% 65% at 50% 100%, rgba(139, 92, 246, 0.38) 0%, rgba(99, 102, 241, 0.22) 35%, rgba(59, 130, 246, 0.08) 55%, transparent 72%)",
          filter: "blur(56px)",
        }}
      />

      {/* Glow arc: яркое «кольцо света» — слой A: мягкий овал */}
      <div
        className="glow-arc-primary absolute left-1/2 top-0 w-[min(118vw,920px)] -translate-x-1/2"
        style={{ height: "min(32vh, 300px)" }}
      />

      {/* Слой B (ribbon) убран: давал заметную горизонтальную полосу при blur */}

      {/* Слой C: conic-дуга (альтернативная реализация — усиливает «корону» над hero) */}
      <div className="glow-arc-conic" aria-hidden />

      {/* Сетка 1px убрана: на длинной странице давала «швы» и горизонтальные стыки */}

      {BLOBS.map((b, i) => (
        <motion.div
          key={i}
          className={`absolute blur-[100px] will-change-transform ${b.className}`}
          style={b.style}
          animate={b.animate}
          transition={b.transition}
        />
      ))}

      {/* Шум (SVG filter — не raster image) */}
      <svg
        className="absolute inset-0 h-full w-full opacity-[0.045] mix-blend-overlay"
        aria-hidden
      >
        <filter id="noiseFilm">
          <feTurbulence
            type="fractalNoise"
            baseFrequency="0.9"
            numOctaves="4"
            stitchTiles="stitch"
          />
        </filter>
        <rect width="100%" height="100%" filter="url(#noiseFilm)" />
      </svg>

      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-[#05020D]/75" />
    </div>
  );
}
