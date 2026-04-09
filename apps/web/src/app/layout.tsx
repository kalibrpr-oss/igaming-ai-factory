import { MeshBackground } from "@/components/background/MeshBackground";
import { SiteShell } from "@/components/layout/SiteShell";
import type { Metadata } from "next";
import { Rubik, JetBrains_Mono } from "next/font/google";
import "@/styles/globals.css";

/** Rubik: одинаково мягко на RU/EN, округлые формы, без «ломаных» пар между алфавитами */
const sans = Rubik({
  subsets: ["latin", "cyrillic"],
  variable: "--font-sans",
  display: "swap",
  weight: ["400", "500", "600", "700"],
});

const mono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
});

export const metadata: Metadata = {
  title: "iGaming AI-Factory",
  description:
    "Высокотехнологичность · Premium · Совершенность — автоматический конвейер SEO-контента для гемблинга",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru">
      <body
        className={`${sans.variable} ${mono.variable} font-sans text-base antialiased`}
      >
        <MeshBackground />
        <div className="relative z-10">
          <SiteShell>{children}</SiteShell>
        </div>
      </body>
    </html>
  );
}
