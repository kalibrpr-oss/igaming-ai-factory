import Link from "next/link";

const tg =
  process.env.NEXT_PUBLIC_TELEGRAM_URL ?? "https://t.me/SetGiftSup";

export function Footer() {
  return (
    <footer className="relative mt-28 border-t border-white/[0.06] bg-[#05020D]">
      <div className="relative mx-auto flex max-w-6xl flex-col gap-10 px-4 py-14 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-lg font-semibold text-zinc-200">
            iGaming <span className="text-gem-bright">AI-Factory</span>
          </p>
          <p className="mt-3 max-w-md text-base leading-relaxed text-zinc-500">
            Генерация SEO-материалов: фокус на iGaming; тематика задаётся в заказе. Позиции в
            выдаче не гарантируем; ответственность за контент — у заказчика.
          </p>
        </div>
        <div className="flex flex-wrap gap-5 text-base text-zinc-400">
          <Link
            href="/guide"
            className="transition-colors duration-[260ms] hover:text-gem-mist"
          >
            Как пользоваться
          </Link>
          <a
            href={tg}
            target="_blank"
            rel="noopener noreferrer"
            className="transition-colors duration-[260ms] hover:text-gem-mist"
          >
            Telegram
          </a>
        </div>
      </div>
      <div className="border-t border-white/[0.04] py-5">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-center gap-3 px-4 text-sm text-zinc-600 sm:flex-row sm:gap-8">
          <span>© {new Date().getFullYear()} iGaming AI-Factory</span>
          <Link
            href="/terms"
            className="text-zinc-500 transition-colors duration-[260ms] hover:text-zinc-400"
          >
            Условия использования
          </Link>
        </div>
      </div>
    </footer>
  );
}
