import { Button } from "@/components/ui/Button";

const steps = [
  {
    n: "01",
    t: "Регистрация",
    d: "Создай аккаунт: email, имя пользователя, пароль. Сразу попадёшь в кабинет.",
  },
  {
    n: "02",
    t: "Заказ",
    d: "Укажи бренд, ключи и LSI, выбери объём слов и голос: Aggressive, Expert или Friendly. Заполни SEO-блок: язык, плотность ключа, структуру заголовков.",
  },
  {
    n: "03",
    t: "Цена и оплата",
    d: "Цена считается автоматически. Дальше подключим ЮMoney/СБП: после оплаты стартанёт генерация.",
  },
  {
    n: "04",
    t: "Выдача",
    d: "Готовый материал уйдёт в .docx на почту (Resend/SendGrid) — настройка на стороне бэкенда.",
  },
];

export default function GuidePage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-20">
      <h1 className="text-4xl font-semibold tracking-tight text-white md:text-5xl">
        Как пользоваться
      </h1>
      <p className="mt-4 text-lg text-zinc-500 md:text-xl">
        Короткий маршрут: от регистрации до файла на почте.
      </p>
      <ol className="mt-12 space-y-8">
        {steps.map((s) => (
          <li key={s.n} className="glass-panel flex gap-5 p-8 md:p-10">
            <span className="font-mono text-base text-gem-bright md:text-lg">{s.n}</span>
            <div>
              <h2 className="text-xl font-semibold text-white md:text-2xl">{s.t}</h2>
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
