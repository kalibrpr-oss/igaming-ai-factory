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
          Заполни ТЗ — цена пересчитается по словам. На первый оплаченный заказ действует
          скидка <span className="text-emerald-200/90">30%</span> (видно в блоке цены, пока
          бонус не использован). После создания — оплата с баланса и генерация.
        </p>
        <div className="mt-10">
          <OrderForm />
        </div>
      </div>
    </AuthGate>
  );
}
