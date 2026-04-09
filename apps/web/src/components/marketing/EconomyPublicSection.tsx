/**
 * Этап дорожной карты: публичное объяснение Credits, скидки и рефералки
 * (без расхождения с логикой бэкенда).
 */
export function EconomyPublicSection() {
  const blocks = [
    {
      title: "Credits и баланс",
      body: (
        <>
          Баланс в кабинете — это внутренние{" "}
          <span className="text-zinc-200">Credits</span> для оплаты генераций.
          Пополняешь через подключённого провайдера; списание — только на заказы.
          Вывода «наличными» нет: валюта сервиса, не электронный кошелёк для
          переводов третьим лицам.
        </>
      ),
    },
    {
      title: "−30% на первый оплаченный заказ",
      body: (
        <>
          На первый заказ, который реально оплачен со счёта (со скидкой по
          правилам сервиса), действует скидка{" "}
          <span className="text-emerald-200/90">30%</span>. Условия и отображение
          суммы — в форме заказа и при входе в аккаунт, пока бонус доступен.
        </>
      ),
    },
    {
      title: "Реферальная программа",
      body: (
        <>
          Делишься ссылкой из кабинета. Если человек зарегистрировался по твоей
          ссылке и пополнил баланс, с{" "}
          <span className="text-zinc-200">первого успешного пополнения</span> ты
          получаешь <span className="text-zinc-200">50%</span> от этой суммы
          (один раз с этого реферала), с каждого следующего его пополнения —{" "}
          <span className="text-zinc-200">15%</span>. Начисления после
          подтверждения платежа, без ручных заявок.
        </>
      ),
    },
  ];

  return (
    <section
      className="border-t border-white/[0.06] bg-pitch-soft/20 px-4 py-20 backdrop-blur-sm md:py-24"
      aria-labelledby="economy-public-heading"
    >
      <div className="mx-auto max-w-6xl">
        <h2
          id="economy-public-heading"
          className="text-center text-3xl font-semibold tracking-tight text-white md:text-4xl"
        >
          Деньги и бонусы — прозрачно
        </h2>
        <p className="mx-auto mt-4 max-w-2xl text-center text-base leading-relaxed text-zinc-500 md:text-lg">
          То же, что видишь в продукте: цифры в кабинете и на странице заказа не
          спорят с этим блоком.
        </p>
        <div className="mt-12 grid gap-6 md:grid-cols-3 md:gap-8">
          {blocks.map((b) => (
            <div
              key={b.title}
              className="liquid-glass liquid-glass-hover flex flex-col p-8 md:p-9"
            >
              <h3 className="text-xl font-semibold text-white md:text-2xl">
                {b.title}
              </h3>
              <p className="mt-4 text-base leading-relaxed text-zinc-400 md:text-lg">
                {b.body}
              </p>
            </div>
          ))}
        </div>
        <p className="mx-auto mt-12 max-w-3xl text-center text-sm leading-relaxed text-zinc-600 md:text-base">
          Позиционирование —{" "}
          <span className="text-zinc-500">iGaming, беттинг, PBN</span> и смежные
          темы. Форму заказа можно использовать и в других нишах: бренд, ключи и
          SEO-параметры задаёшь ты, ответственность за публикацию и compliance —
          на стороне клиента.
        </p>
      </div>
    </section>
  );
}
