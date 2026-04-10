import { BrandVoicesSectionPremium } from "@/components/marketing/BrandVoicesSectionPremium";
import { EconomyPublicSection } from "@/components/marketing/EconomyPublicSection";
import { Hero } from "@/components/marketing/Hero";
import { HomeBottomCta } from "@/components/marketing/HomeBottomCta";
import { Reviews } from "@/components/marketing/Reviews";

export default function HomePage() {
  return (
    <>
      <Hero />
      <BrandVoicesSectionPremium />
      <section className="border-t border-white/[0.04] px-4 py-20">
        <div className="mx-auto grid max-w-6xl gap-8 md:grid-cols-3 md:gap-10">
          {[
            {
              t: "ТЗ в одной форме",
              d: "Бренд, ключи, LSI, плотность, язык, тип материала — единый набор полей для любой ниши.",
            },
            {
              t: "Три голоса",
              d: "Aggressive, Expert, Friendly. Три стиля подачи на выбор.",
            },
            {
              t: "Цена видна сразу",
              d: "Считаем по объёму и пресету; на первый оплаченный заказ — скидка 30%, если бонус ещё активен. Без скрытых доплат в форме.",
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
      <EconomyPublicSection />
      <Reviews />
      <HomeBottomCta />
    </>
  );
}
