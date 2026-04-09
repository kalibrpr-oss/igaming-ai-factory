import type { Transition, Variants } from "framer-motion";

/** Spring как у «премиальных» интерфейсов: чуть упругий, без пружины-качели */
export const springReveal: Transition = {
  type: "spring",
  stiffness: 380,
  damping: 28,
  mass: 0.8,
};

export const springSoft: Transition = {
  type: "spring",
  stiffness: 220,
  damping: 22,
};

export const fadeUp: Variants = {
  hidden: { opacity: 0, y: 18 },
  visible: {
    opacity: 1,
    y: 0,
    transition: springReveal,
  },
};

/** Premium: fade + лёгкий scale, 200–300ms, ease material */
export const fadeScale: Variants = {
  hidden: { opacity: 0, y: 20, scale: 0.985 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { duration: 0.28, ease: [0.4, 0, 0.2, 1] },
  },
};

export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1, delayChildren: 0.06 },
  },
};

export const cardLift: Variants = {
  hidden: { opacity: 0, y: 20, scale: 0.99 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { duration: 0.28, ease: [0.4, 0, 0.2, 1] },
  },
};
