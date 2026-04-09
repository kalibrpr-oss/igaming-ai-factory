import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        pitch: {
          DEFAULT: "#000000",
          soft: "#030306",
          card: "#050508",
        },
        void: "#05020D",
        ink: {
          950: "#020203",
          900: "#050508",
          800: "#0a0a0f",
          700: "#12121a",
        },
        gem: {
          DEFAULT: "#10b981",
          bright: "#34d399",
          mist: "#6ee7b7",
          deep: "#047857",
          glow: "#a7f3d0",
        },
        neon: {
          violet: "#a855f7",
          indigo: "#6366f1",
          blue: "#3b82f6",
        },
        accent: {
          DEFAULT: "#8b5cf6",
          dim: "#6d28d9",
          glow: "#a78bfa",
        },
        surface: "rgba(255,255,255,0.03)",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      boxShadow: {
        glass:
          "inset 0 1px 0 0 rgba(255, 255, 255, 0.1), inset 0 -1px 0 0 rgba(0, 0, 0, 0.35)",
        "emerald-glow":
          "0 0 0 1px rgba(52, 211, 153, 0.15), 0 0 48px -12px rgba(16, 185, 129, 0.45)",
        "emerald-glow-lg":
          "0 0 80px -20px rgba(16, 185, 129, 0.55), 0 0 0 1px rgba(52, 211, 153, 0.2)",
        "neon-violet":
          "0 0 0 1px rgba(139, 92, 246, 0.25), 0 0 56px -12px rgba(139, 92, 246, 0.55)",
        lift: "0 24px 80px -32px rgba(0, 0, 0, 0.75)",
      },
      backgroundImage: {
        "mesh-emerald":
          "radial-gradient(ellipse 100% 80% at 50% -30%, rgba(139, 92, 246, 0.18), transparent 55%), radial-gradient(ellipse 60% 50% at 100% 0%, rgba(52, 211, 153, 0.1), transparent 45%), radial-gradient(ellipse 50% 40% at 0% 100%, rgba(59, 130, 246, 0.12), transparent 50%)",
        "shine-sweep":
          "linear-gradient(105deg, transparent 40%, rgba(255,255,255,0.12) 50%, transparent 60%)",
      },
      keyframes: {
        "shine-slide": {
          "0%": { transform: "translateX(-120%) skewX(-12deg)" },
          "100%": { transform: "translateX(220%) skewX(-12deg)" },
        },
        "pulse-emerald": {
          "0%, 100%": { opacity: "0.4" },
          "50%": { opacity: "1" },
        },
      },
      animation: {
        "shine-slide": "shine-slide 2.2s ease-in-out infinite",
        "pulse-emerald": "pulse-emerald 2s ease-in-out infinite",
      },
      transitionDuration: {
        DEFAULT: "260ms",
        250: "250ms",
      },
      transitionTimingFunction: {
        smooth: "cubic-bezier(0.4, 0, 0.2, 1)",
      },
    },
  },
  plugins: [],
};

export default config;
