"use client";

import { setReferralFromQuery } from "@/lib/referral-cookie";
import { useSearchParams } from "next/navigation";
import { useEffect } from "react";

/** Ловит ?ref= на любой странице и кладёт код в cookie для регистрации. */
export function ReferralCapture() {
  const sp = useSearchParams();
  useEffect(() => {
    setReferralFromQuery(sp.get("ref"));
  }, [sp]);
  return null;
}
