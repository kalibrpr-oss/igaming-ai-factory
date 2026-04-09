const KEY = "access_token";

type PostAuthRouter = {
  push: (href: string) => void;
};

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(KEY);
}

export function completeAuthSuccess(
  router: PostAuthRouter,
  token: string
): void {
  setToken(token);
  router.push("/dashboard");
}
