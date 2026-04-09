import { Button } from "@/components/ui/Button";

const steps = [
  {
    n: "01",
    t: "Регистрация и почта",
    d: "Аккаунт: email, имя пользователя, пароль. После регистрации подтверди почту по ссылке из письма — без этого вход и заказы недоступны.",
  },
  {
    n: "02",
    t: "Заказ",
    d: "Бренд, ключи и LSI, объём слов, голос (Aggressive, Expert, Friendly), блок SEO: язык, плотность, заголовки. Залогиненному покажем цену с учётом скидки на первый оплаченный заказ, если она ещё действует.",
  },
  {
    n: "03",
    t: "Баланс и оплата",
    d: "Пополняешь баланс (Credits) через подключённого провайдера; в разработке доступен тестовый контур. Оплата заказа — со счёта в кабинете. После успешной оплаты запускаешь генерацию из карточки заказа.",
  },
  {
    n: "04",
    t: "Результат и рефералка",
    d: "Статус заказа и текст — в кабинете. В ЛК есть реферальная ссылка: бонусы с пополнений приглашённых начисляются автоматически после подтверждения платежа (50% с первого пополнения реферала, далее 15% — см. кабинет и главную).",
  },
];

export default function GuidePage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-20">
      <h1 className="text-4xl font-semibold tracking-tight text-white md:text-5xl">
        Как пользоваться
      </h1>
      <p className="mt-4 text-lg text-zinc-500 md:text-xl">
        От регистрации до генерации: без лишних шагов.
      </p>
      <ol className="mt-12 space-y-8">
        {steps.map((s) => (
          <li key={s.n} className="glass-panel flex gap-5 p-8 md:p-10">
            <span className="font-mono text-base text-gem-bright md:text-lg">
              {s.n}
            </span>
            <div>
              <h2 className="text-xl font-semibold text-white md:text-2xl">
                {s.t}
              </h2>
              <p className="mt-2 text-base leading-relaxed text-zinc-400 md:text-lg">
                {s.d}
              </p>
            </div>
          </li>
        ))}
      </ol>
      <div className="mt-10 flex flex-wrap gap-3">
        <Button href="/register">Регистрация</Button>
        <Button variant="outline" href="/order">
          К форме заказа
        </Button>
      </div>
    </div>
  );
}
