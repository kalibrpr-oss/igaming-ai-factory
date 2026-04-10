import { Button } from "@/components/ui/Button";
import { GradientHeading } from "@/components/ui/GradientHeading";
import Link from "next/link";

const blocks = [
  {
    n: "01",
    t: "Регистрация и почта",
    d: "Email, имя пользователя, пароль. После регистрации — подтверждение почты по ссылке из письма; без него вход и заказы недоступны.",
  },
  {
    n: "02",
    t: "Заказ",
    d: "Бренд, ключи, LSI, объём, голос (Aggressive, Expert, Friendly), SEO-блок: язык, плотность, заголовки. Для авторизованного пользователя цена с учётом скидки на первый оплаченный заказ — при активном бонусе.",
  },
  {
    n: "03",
    t: "Баланс и оплата",
    d: "Пополнение баланса (Credits) — через подключённого провайдера; в разработке — тестовый контур. Оплата заказа с баланса. После успешной оплаты — запуск генерации из карточки заказа.",
  },
  {
    n: "04",
    t: "Результат и рефералка",
    d: "Статус и материалы — в кабинете. Реферальная ссылка в ЛК; бонусы с пополнений приглашённых — после подтверждения платежа (50% с первого пополнения реферала, далее 15%; детали — в кабинете и на главной).",
  },
];

export default function GuidePage() {
  return (
    <div className="mx-auto max-w-6xl px-4 py-20">
      <GradientHeading
        as="h1"
        className="text-4xl font-bold tracking-tight md:text-5xl"
      >
        Как пользоваться
      </GradientHeading>

      <section className="mt-10 glass-panel p-8 md:p-10" aria-labelledby="guide-about-heading">
        <h2
          id="guide-about-heading"
          className="text-[1.65rem] font-semibold tracking-[-0.02em] text-white sm:text-3xl md:text-[1.875rem]"
        >
          Что это за сервис?
        </h2>
        <div className="mt-8 w-full max-w-none space-y-6 text-lg leading-[1.7] text-zinc-300 md:text-xl md:leading-[1.75]">
          <p>
            Это генератор, который создаёт уникальные и качественные тексты по вашим параметрам.
            Подходит для статей под сайты в разных тематиках; чаще всего заказывают под казино и
            партнёрские программы. В форме заказа есть поля: название бренда, ключевые и
            вспомогательные слова, объём в словах, заголовки и другие настройки. Готовый текст
            приходит файлом <span className="text-violet-200/90">.docx</span> на вашу почту —
            обычно в течение 10 минут.
          </p>
          <p>
            Три фирменных стиля подачи: Aggressive, Expert, Friendly. Их можно бесплатно
            проверить{" "}
            <Link
              href="/#demo-brand-voices"
              className="text-violet-200/95 underline decoration-violet-500/40 underline-offset-2 transition-colors hover:text-violet-100 hover:decoration-violet-300/60"
            >
              на главной странице
            </Link>
            .
          </p>
          <p>
            Действует{" "}
            <Link
              href="#referral-program"
              className="text-violet-200/95 underline decoration-violet-500/40 underline-offset-2 transition-colors hover:text-violet-100 hover:decoration-violet-300/60"
            >
              реферальная
            </Link>{" "}
            программа и внутренняя валюта на балансе — в том числе за приглашённых пользователей.
            С баланса оплачиваются заказы; средства с пополнений и бонусов суммируются на одном
            счёте.
          </p>
          <p className="text-zinc-400">
            Цену видно до оплаты, статус заказа — в личном кабинете.
          </p>
        </div>
      </section>

      <h2 className="mt-16 text-2xl font-semibold tracking-tight text-white md:text-3xl">
        Пошагово: от аккаунта до текста
      </h2>
      <p className="mt-3 max-w-2xl text-base text-zinc-500 md:text-lg">
        Регистрация, заказ, оплата, получение результата.
      </p>
      <ul className="mt-10 grid list-none grid-cols-1 gap-6 md:grid-cols-2 md:gap-8">
        {blocks.map((s) => (
          <li
            key={s.n}
            id={s.n === "04" ? "referral-program" : undefined}
            className="glass-panel flex min-h-[220px] scroll-mt-24 flex-col p-8 md:min-h-[240px] md:p-9"
          >
            <span className="heading-shimmer inline-block text-2xl font-semibold leading-none tracking-[-0.04em] text-transparent [font-feature-settings:normal] [font-variant-numeric:normal] md:text-[1.85rem]">
              {s.n}
            </span>
            <h3 className="mt-3 text-xl font-semibold text-white md:text-2xl">
              {s.t}
            </h3>
            <p className="mt-3 flex-1 text-base leading-relaxed text-zinc-400 md:text-lg">
              {s.d}
            </p>
          </li>
        ))}
      </ul>
      <div className="mt-10 flex flex-wrap gap-3">
        <Button href="/register">Регистрация</Button>
        <Button variant="outline" href="/order">
          К форме заказа
        </Button>
      </div>
    </div>
  );
}
