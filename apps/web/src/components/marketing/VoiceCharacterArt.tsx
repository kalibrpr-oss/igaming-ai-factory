"use client";

import { cn } from "@/lib/cn";
import type { BrandVoiceId } from "@/types";

/** Абстрактные «персонажи» без внешних ассетов: чистый CSS + SVG, GTA / anime / sci-fi вайб. */

export function VoiceCharacterArt({
  voiceId,
  className,
}: {
  voiceId: BrandVoiceId;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "relative mx-auto flex h-48 w-full max-w-[240px] items-end justify-center overflow-hidden rounded-2xl md:h-52 md:max-w-[260px]",
        className
      )}
    >
      {voiceId === "bold_daring" && <ArtAggressive />}
      {voiceId === "friendly_warm" && <ArtFriendly />}
      {voiceId === "expert_precise" && <ArtExpert />}
    </div>
  );
}

function ArtAggressive() {
  return (
    <div className="relative h-full w-full bg-gradient-to-b from-emerald-950/80 to-pitch-soft">
      {/* силуэт «улица / GTA»: козырёк, плечи, закат */}
      <div className="absolute inset-x-4 bottom-0 h-24 rounded-t-2xl bg-gradient-to-t from-zinc-900 to-zinc-800 shadow-[0_0_30px_rgba(16,185,129,0.35)]" />
      <div className="absolute bottom-20 left-1/2 h-14 w-20 -translate-x-1/2 rounded-full bg-gradient-to-br from-amber-700/90 to-amber-950" />
      <div className="absolute bottom-[5.5rem] left-1/2 h-8 w-24 -translate-x-1/2 rounded-t-full bg-zinc-900 shadow-[inset_0_-4px_0_0_rgba(16,185,129,0.4)]" />
      <div className="absolute right-6 top-6 h-2 w-10 rotate-12 rounded-full bg-emerald-400/80 blur-[2px]" />
      <div className="absolute left-4 top-8 h-px w-16 bg-gradient-to-r from-transparent via-emerald-400/50 to-transparent" />
    </div>
  );
}

function ArtFriendly() {
  return (
    <div className="relative h-full w-full bg-gradient-to-b from-fuchsia-950/40 to-pitch-soft">
      <div className="absolute inset-x-8 bottom-0 h-20 rounded-t-[2rem] bg-gradient-to-t from-emerald-900/60 to-emerald-800/30" />
      <div className="absolute bottom-16 left-1/2 flex -translate-x-1/2 gap-2">
        <div className="h-10 w-10 rounded-full bg-gradient-to-br from-pink-300/90 to-rose-400/80 shadow-[0_0_20px_rgba(52,211,153,0.45)]" />
        <div className="h-10 w-10 rounded-full bg-gradient-to-br from-pink-300/90 to-rose-400/80 shadow-[0_0_20px_rgba(52,211,153,0.45)]" />
      </div>
      <div className="absolute bottom-[4.5rem] left-1/2 h-16 w-16 -translate-x-1/2 rounded-full bg-gradient-to-b from-rose-200/90 to-rose-400/70" />
      <div className="absolute bottom-[6.25rem] left-[42%] h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_8px_#34d399]" />
      <div className="absolute bottom-[6.25rem] right-[42%] h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_8px_#34d399]" />
    </div>
  );
}

function ArtExpert() {
  return (
    <div className="relative h-full w-full bg-gradient-to-b from-cyan-950/50 to-pitch-soft">
      <div className="absolute inset-x-6 bottom-0 h-16 rounded-lg border border-emerald-500/30 bg-pitch/80 backdrop-blur-sm" />
      <div className="absolute bottom-14 left-1/2 h-20 w-16 -translate-x-1/2 rounded-md border border-emerald-400/40 bg-gradient-to-b from-slate-800 to-slate-950">
        <div className="mx-auto mt-4 h-6 w-10 rounded border border-cyan-400/40 bg-cyan-500/20" />
      </div>
      <div className="absolute bottom-[5.5rem] left-1/2 h-10 w-12 -translate-x-1/2 rounded-full bg-gradient-to-b from-slate-600 to-slate-900" />
      <div className="absolute left-8 top-6 flex gap-1">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="h-6 w-1 rounded-full bg-emerald-500/60"
            style={{ animationDelay: `${i * 0.15}s` }}
          />
        ))}
      </div>
      <div className="absolute right-6 top-10 h-8 w-8 rounded-full border border-emerald-400/30 bg-emerald-500/10" />
    </div>
  );
}
