/** Имя cookie для кода пригласившего (совпадает с ?ref=). */
export const REFERRAL_COOKIE_NAME = "ig_ref";

const MAX_AGE_SEC = 60 * 60 * 24 * 90; // 90 дней

/** Сохранить ref из query (?ref=) в cookie (первый заход по ссылке). */
export function setReferralFromQuery(ref: string | null): void {
  if (typeof document === "undefined" || !ref) return;
  const v = ref.trim().toLowerCase();
  if (!v || v.length > 32) return;
  document.cookie = `${REFERRAL_COOKIE_NAME}=${encodeURIComponent(v)};path=/;max-age=${MAX_AGE_SEC};SameSite=Lax`;
}

/** Прочитать сохранённый код для отправки при регистрации. */
export function getReferralCookie(): string | undefined {
  if (typeof document === "undefined") return undefined;
  const parts = document.cookie.split(";").map((p) => p.trim());
  for (const p of parts) {
    if (p.startsWith(`${REFERRAL_COOKIE_NAME}=`)) {
      const raw = p.slice(REFERRAL_COOKIE_NAME.length + 1);
      try {
        const v = decodeURIComponent(raw).trim().toLowerCase();
        return v || undefined;
      } catch {
        return undefined;
      }
    }
  }
  return undefined;
}
