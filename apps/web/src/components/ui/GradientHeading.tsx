import { cn } from "@/lib/cn";
import type { ReactNode } from "react";

/** Заголовок с едва заметным «дышащим» градиентом (CSS, GPU). */
export function GradientHeading({
  children,
  className,
  as: Tag = "h2",
}: {
  children: ReactNode;
  className?: string;
  as?: "h1" | "h2" | "h3";
}) {
  return (
    <Tag
      className={cn(
        "heading-shimmer font-semibold tracking-[-0.02em] text-transparent",
        className
      )}
    >
      {children}
    </Tag>
  );
}
