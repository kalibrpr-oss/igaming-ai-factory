import { Footer } from "@/components/layout/Footer";
import { Header } from "@/components/layout/Header";
import { ReferralCapture } from "@/components/layout/ReferralCapture";
import { Suspense } from "react";

export function SiteShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-dvh flex-col">
      <Suspense fallback={null}>
        <ReferralCapture />
      </Suspense>
      <Header />
      <div className="flex-1">{children}</div>
      <Footer />
    </div>
  );
}
