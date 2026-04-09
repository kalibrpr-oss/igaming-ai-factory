/** Правила ника при регистрации (как на бэкенде): латиница + цифры, 4–15 символов. */

export function validateUsername(raw: string): string | null {
  const s = raw.trim();
  if (s.length < 4) {
    return "Ник слишком короткий — нужно от 4 до 15 символов.";
  }
  if (s.length > 15) {
    return "Ник слишком длинный — максимум 15 символов.";
  }
  if (!/^[a-zA-Z0-9]+$/.test(s)) {
    return "Ник: только английские буквы и цифры, без пробелов и других знаков.";
  }
  return null;
}
