import { cn } from "@/lib/cn";
import Image from "next/image";

/** Публичный путь: положите файл в `public/icons/sparkles.png`. */
const SPARKLES_SRC = "/icons/sparkles.png";

/** Видимый размер иконки в UI (квадрат). */
const ICON_PX = 28;

type SparklesPngIconProps = {
  className?: string;
};

/**
 * PNG «sparkles»: object-contain, центр, лёгкий glow.
 * Исходник может быть большим — в квадрате ICON_PX (см. константу выше).
 */
export function SparklesPngIcon({ className }: SparklesPngIconProps) {
  return (
    <span
      className={cn(
        "pointer-events-none relative inline-flex shrink-0",
        "items-center justify-center overflow-hidden",
        className
      )}
      style={{
        width: ICON_PX,
        height: ICON_PX,
        minWidth: ICON_PX,
        minHeight: ICON_PX,
      }}
      aria-hidden
    >
      <Image
        src={SPARKLES_SRC}
        alt=""
        fill
        sizes={`${ICON_PX}px`}
        className={cn(
          "object-contain object-center",
          "origin-center scale-[1.06]",
          "[filter:drop-shadow(0_0_4px_rgba(167,243,208,0.22))]"
        )}
      />
    </span>
  );
}

/** Только для кнопок «30 слов бесплатно»: иконка слева, почти впритык к тексту. */
export function FreeWordsButtonLabel() {
  return (
    <span className="inline-flex items-center justify-center gap-0">
      <SparklesPngIcon className="-mr-0.5" />
      30 слов бесплатно
    </span>
  );
}
