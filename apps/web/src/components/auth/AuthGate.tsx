"use client";

import { fetchMe } from "@/api/endpoints";
import { clearToken, getToken } from "@/lib/auth-storage";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

/** Редирект на логин без токена; без подтверждённого email — на страницу подтверждения. */
export function AuthGate({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.replace("/login");
      return;
    }

    let cancelled = false;
    fetchMe()
      .then((user) => {
        if (cancelled) return;
        if (!user.is_email_verified) {
          clearToken();
          router.replace(
            `/verify-email?email=${encodeURIComponent(user.email)}`
          );
          return;
        }
        setReady(true);
      })
      .catch(() => {
        if (cancelled) return;
        clearToken();
        router.replace("/login");
      });

    return () => {
      cancelled = true;
    };
  }, [router]);

  if (!ready) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center text-sm text-zinc-500">
        Проверка сессии…
      </div>
    );
  }

  return <>{children}</>;
}
