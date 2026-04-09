"use client";

import { cn } from "@/lib/cn";
import Link from "next/link";
import type { ComponentProps } from "react";
import { useCallback } from "react";

type Variant = "primary" | "ghost" | "outline";

const variants: Record<Variant, string> = {
  primary:
    "bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 text-white shadow-neon-violet " +
    "hover:brightness-110 hover:shadow-[0_0_56px_-8px_rgba(139,92,246,0.65)] hover:scale-[1.03] " +
    "active:scale-[0.98] active:brightness-95",
  ghost:
    "bg-white/[0.05] text-zinc-100 border border-white/10 backdrop-blur-md " +
    "hover:bg-white/[0.09] hover:border-white/20 hover:scale-[1.02] active:scale-[0.98]",
  outline:
    "border border-white/15 bg-transparent text-zinc-100 backdrop-blur-sm " +
    "hover:border-violet-400/40 hover:bg-violet-500/10 hover:shadow-neon-violet hover:scale-[1.02] active:scale-[0.98]",
};

export function Button({
  className,
  variant = "primary",
  href,
  type = "button",
  children,
  primaryCta = false,
  onPointerDown,
  ...rest
}: ComponentProps<"button"> & {
  variant?: Variant;
  href?: string;
  /** Мягкий click-ripple только для главных CTA (не для всех кнопок) */
  primaryCta?: boolean;
}) {
  const cls = cn(
    "btn-cta-sweep inline-flex min-h-[52px] items-center justify-center gap-2.5 rounded-full px-9 py-4 text-lg font-medium tracking-wide transition-all duration-250 ease-smooth",
    primaryCta && "btn-cta-ripple",
    variants[variant],
    className
  );

  const handlePointerDown = useCallback(
    (e: React.PointerEvent<HTMLButtonElement & HTMLAnchorElement>) => {
      onPointerDown?.(e);
      if (!primaryCta || e.button !== 0) return;
      const el = e.currentTarget;
      const rect = el.getBoundingClientRect();
      el.style.setProperty("--ripple-x", `${e.clientX - rect.left}px`);
      el.style.setProperty("--ripple-y", `${e.clientY - rect.top}px`);
      el.classList.remove("btn-ripple-play");
      void el.offsetWidth;
      el.classList.add("btn-ripple-play");
      window.setTimeout(() => {
        el.classList.remove("btn-ripple-play");
      }, 580);
    },
    [onPointerDown, primaryCta]
  );

  const inner = (
    <span className="relative z-[1] inline-flex items-center justify-center gap-2.5">
      {children}
    </span>
  );
  if (href) {
    /* Link не принимает пропсы <button> (type, disabled, …) — не пробрасываем rest */
    return (
      <Link href={href} className={cls} onPointerDown={handlePointerDown}>
        {inner}
      </Link>
    );
  }
  return (
    <button
      type={type}
      className={cls}
      onPointerDown={handlePointerDown}
      {...rest}
    >
      {inner}
    </button>
  );
}
