import { BrandVoicesSectionPremium } from "@/components/marketing/BrandVoicesSectionPremium";
import { Hero } from "@/components/marketing/Hero";
import { Reviews } from "@/components/marketing/Reviews";
import { Button } from "@/components/ui/Button";

export default function HomePage() {
  return (
    <>
      <Hero />
      <BrandVoicesSectionPremium />
      <section className="bg-pitch-soft/30 px-4 py-20 backdrop-blur-sm">
        <div className="mx-auto grid max-w-6xl gap-8 md:grid-cols-3 md:gap-10">
          {[
            {
              t: "ТЗ в одной форме",
              d: "Бренд, ключи, LSI, плотность, язык, тип статьи. Всё уходит в генерацию.",
            },
            {
              t: "Три голоса",
              d: "Aggressive, Expert, Friendly. Три стиля подачи на выбор.",
            },
            {
              t: "Цена видна сразу",
              d: "Платишь только за текст. Фикс за каждые 100 слов, без скрытых доплат.",
            },
          ].map((x) => (
            <div key={x.t} className="liquid-glass liquid-glass-hover p-8 md:p-9">
              <h3 className="text-xl font-semibold text-white md:text-2xl">{x.t}</h3>
              <p className="mt-4 text-base leading-relaxed text-zinc-400 md:text-lg">
                {x.d}
              </p>
            </div>
          ))}
        </div>
      </section>
      <Reviews />
      <section className="px-4 pb-28">
        <div className="liquid-glass mx-auto max-w-4xl p-10 text-center shadow-emerald-glow md:p-12">
          <h2 className="text-3xl font-semibold text-white md:text-4xl">
            Готов прогнать материал?
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-base text-zinc-400 md:text-lg">
            Регистрация — пара полей. Потом форма заказа и оплата (подключим на следующем
            этапе).
          </p>
          <div className="mt-10 flex flex-wrap justify-center gap-4">
            <Button href="/register" primaryCta>
              Создать аккаунт
            </Button>
            <Button variant="outline" href="/order">
              Уже есть логин — к заказу
            </Button>
          </div>
        </div>
      </section>
    </>
  );
}
