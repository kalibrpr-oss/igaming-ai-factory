/** Утилиты общего назначения; позже: cn() с clsx/tailwind-merge */
export function assertEnv(name: string): string {
  const v = process.env[name];
  if (!v) throw new Error(`Отсутствует переменная окружения: ${name}`);
  return v;
}
