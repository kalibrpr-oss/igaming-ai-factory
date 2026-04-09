import enum


class EmailVerificationPurpose(str, enum.Enum):
    verify_email = "verify_email"


class PaymentKind(str, enum.Enum):
    order_payment = "order_payment"
    wallet_topup = "wallet_topup"


class BalanceTransactionType(str, enum.Enum):
    topup = "topup"
    order_debit = "order_debit"
    referral_reward = "referral_reward"
    adjustment = "adjustment"


class BalanceReferenceType(str, enum.Enum):
    payment = "payment"
    order = "order"
    manual = "manual"


class OrderStatus(str, enum.Enum):
    draft = "draft"
    pending_payment = "pending_payment"
    paid = "paid"
    generating = "generating"
    review_required = "review_required"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class PaymentProvider(str, enum.Enum):
    yoomoney = "yoomoney"
    sbp = "sbp"
    mock = "mock"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    succeeded = "succeeded"
    failed = "failed"
    refunded = "refunded"
