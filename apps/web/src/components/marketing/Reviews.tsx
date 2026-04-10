"use client";

import { cardLift, staggerContainer } from "@/lib/motion";
import { motion } from "framer-motion";

const items = [
  {
    name: "Артём · сетка 40+ сайтов",
    text: "Фриланс не выдерживал объём и сроки. Сервис даёт единый формат ТЗ, оплату по счёту и файл на почту — удобно для массовых задач.",
  },
  {
    name: "Марина · SEO-агентство",
    text: "Нужны были обзоры под разные бренды. Три пресета голоса сокращают цикл правок.",
  },
  {
    name: "Илья · арбитраж",
    text: "Счётчик слов и цена до оплаты отображаются явно. Результат приходит на почту без участия менеджера.",
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
          Позиции в выдаче не гарантируем.
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
