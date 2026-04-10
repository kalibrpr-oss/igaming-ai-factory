import { AuthGate } from "@/components/auth/AuthGate";
import { OrderForm } from "@/features/order-form/OrderForm";

export default function OrderPage() {
  return (
    <AuthGate>
      <div className="mx-auto max-w-6xl px-4 py-16 md:py-20">
        <h1 className="text-3xl font-semibold tracking-tight text-white md:text-4xl">
          Новый заказ
        </h1>
        <p className="mt-3 max-w-2xl text-base text-zinc-500 md:text-lg">
          Заполнение ТЗ — пересчёт цены по объёму. Скидка{" "}
          <span className="text-emerald-200/90">30%</span> на первый оплаченный заказ
          (блок цены, пока бонус активен). После создания заказа — оплата с баланса и
          генерация.
        </p>
        <div className="mt-10">
          <OrderForm />
        </div>
      </div>
    </AuthGate>
  );
}
