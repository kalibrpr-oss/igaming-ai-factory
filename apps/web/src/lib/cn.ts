import clsx, { type ClassValue } from "clsx";

/** Склейка классов для Tailwind */
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}
