"use client";

import { cardLift, staggerContainer } from "@/lib/motion";
import { motion } from "framer-motion";

const items = [
  {
    name: "Артём · сетка 40+ сайтов",
    text: "Раньше тонну текста закрывали фрилансом, сроки плавали. Здесь закинул ТЗ, оплатил, файл прилетел. Для массовки норм.",
  },
  {
    name: "Марина · SEO-агентство",
    text: "Нужны были обзоры под бренды с разным тоном. Три пресета голоса реально экономят время на правках.",
  },
  {
    name: "Илья · арбитраж",
    text: "Счётчик слов и цена до оплаты. Всё прозрачно. Дальше жду авто-отправку на почту без менеджеров.",
  },
];

export function Reviews() {
  return (
    <section className="px-4 py-20">
      <div className="mx-auto max-w-6xl">
        <h2 className="text-center text-3xl font-semibold text-white sm:text-4xl md:text-5xl">
          Отзывы клиентов
        </h2>
        <p className="mx-auto mt-4 max-w-2xl text-center text-base text-zinc-500 md:text-lg">
          Формат отзывов рабочий. Мы не обещаем «гарантированный топ».
        </p>
        <motion.div
          className="mt-12 grid gap-6 md:grid-cols-3"
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-60px" }}
        >
          {items.map((r) => (
            <motion.article
              key={r.name}
              variants={cardLift}
              className="group liquid-glass liquid-glass-hover p-8 md:p-9"
            >
              <p className="text-base leading-relaxed text-zinc-300 md:text-lg">
                {r.text}
              </p>
              <p className="mt-6 text-sm font-medium text-gem-bright/90">{r.name}</p>
            </motion.article>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
