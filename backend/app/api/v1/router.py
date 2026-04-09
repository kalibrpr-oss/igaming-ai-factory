from fastapi import APIRouter

from app.api.v1 import (
    admin_orders,
    admin_payments,
    admin_users,
    auth,
    brand_voices,
    demo_rewrite,
    health,
    orders,
    referral,
    wallet_user,
)
from app.config import settings

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(brand_voices.router, prefix="/brand-voices", tags=["brand-voices"])
api_router.include_router(
    demo_rewrite.router, prefix="/demo", tags=["demo"]
)
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(wallet_user.router, prefix="/wallet", tags=["wallet"])
api_router.include_router(referral.router, prefix="/referral", tags=["referral"])
api_router.include_router(
    admin_users.router, prefix="/admin/users", tags=["admin-users"]
)
api_router.include_router(
    admin_orders.router, prefix="/admin/orders", tags=["admin-orders"]
)
api_router.include_router(
    admin_payments.router, prefix="/admin/payments", tags=["admin-payments"]
)

if settings.enable_internal_wallet_test_flow:
    from app.api.v1 import internal_wallet_test

    api_router.include_router(
        internal_wallet_test.router,
        prefix="/internal/wallet-test",
        tags=["internal-wallet-test"],
    )
