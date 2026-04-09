"use client";

import { fetchMe } from "@/api/endpoints";
import { AuthGate } from "@/components/auth/AuthGate";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

function AdminShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [ok, setOk] = useState<boolean | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchMe()
      .then((me) => {
        if (cancelled) return;
        if (!me.is_admin) {
          router.replace("/dashboard");
          return;
        }
        setOk(true);
      })
      .catch(() => {
        if (cancelled) return;
        router.replace("/login");
      });
    return () => {
      cancelled = true;
    };
  }, [router]);

  if (ok !== true) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center text-sm text-zinc-500">
        Проверка прав администратора…
      </div>
    );
  }

  return (
    <>
      <nav className="border-b border-white/[0.08] bg-black/30 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-4 px-4 py-3 text-sm">
          <span className="font-medium text-zinc-400">Админка</span>
          <Link
            href="/admin"
            className="text-zinc-300 transition-colors hover:text-white"
          >
            Обзор
          </Link>
          <Link
            href="/admin/users"
            className="text-zinc-300 transition-colors hover:text-white"
          >
            Пользователи
          </Link>
          <Link
            href="/admin/payments"
            className="text-zinc-300 transition-colors hover:text-white"
          >
            Платежи
          </Link>
          <Link
            href="/dashboard"
            className="ml-auto text-zinc-500 transition-colors hover:text-zinc-300"
          >
            В кабинет
          </Link>
        </div>
      </nav>
      {children}
    </>
  );
}

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthGate>
      <AdminShell>{children}</AdminShell>
    </AuthGate>
  );
}
