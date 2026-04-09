from fastapi import APIRouter

from app.api.v1 import (
    admin_orders,
    admin_users,
    auth,
    brand_voices,
    demo_rewrite,
    health,
    orders,
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
api_router.include_router(
    admin_users.router, prefix="/admin/users", tags=["admin-users"]
)
api_router.include_router(
    admin_orders.router, prefix="/admin/orders", tags=["admin-orders"]
)

if settings.enable_internal_wallet_test_flow:
    from app.api.v1 import internal_wallet_test

    api_router.include_router(
        internal_wallet_test.router,
        prefix="/internal/wallet-test",
        tags=["internal-wallet-test"],
    )
