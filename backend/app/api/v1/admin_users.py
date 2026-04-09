from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.dependencies import get_current_admin
from app.models.balance_transaction import BalanceTransaction
from app.models.enums import BalanceTransactionType, PaymentStatus
from app.models.order import Order
from app.models.payment import Payment
from app.models.user import User
from app.schemas.admin import (
    AdminGrantCreditsBody,
    AdminGrantCreditsResponse,
    AdminOrderBrief,
    AdminReferralInviteRow,
    AdminUserBrief,
    AdminUserDetail,
    AdminUserPatchBody,
    AdminUserRow,
)
from app.services.admin_credits import AdminCreditsError, grant_credits_by_admin
from app.services.user_activity import device_kind_from_user_agent

router = APIRouter()


@router.get("", response_model=list[AdminUserRow])
async def list_users_with_stats(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
) -> list[AdminUserRow]:
    users_result = await session.execute(
        select(User).order_by(User.created_at.desc())
    )
    users = list(users_result.scalars().all())
    if not users:
        return []

    ids = [u.id for u in users]
    order_counts = await session.execute(
        select(Order.user_id, func.count(Order.id))
        .where(Order.user_id.in_(ids))
        .group_by(Order.user_id)
    )
    oc_map = {row[0]: row[1] for row in order_counts.all()}

    pay_counts = await session.execute(
        select(Payment.user_id, func.count(Payment.id))
        .where(
            Payment.user_id.in_(ids),
            Payment.status == PaymentStatus.succeeded,
        )
        .group_by(Payment.user_id)
    )
    pc_map = {row[0]: row[1] for row in pay_counts.all()}

    return [
        AdminUserRow(
            id=u.id,
            email=u.email,
            username=u.username,
            created_at=u.created_at,
            is_active=u.is_active,
            is_admin=u.is_admin,
            orders_total=oc_map.get(u.id, 0),
            payments_succeeded=pc_map.get(u.id, 0),
            last_seen_at=u.last_seen_at,
            last_device_kind=device_kind_from_user_agent(u.last_user_agent),
        )
        for u in users
    ]


@router.get("/{user_id}", response_model=AdminUserDetail)
async def get_user_detail(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
) -> AdminUserDetail:
    u = await session.get(User, user_id)
    if u is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    referrer_brief: AdminUserBrief | None = None
    if u.referrer_user_id is not None:
        ref = await session.get(User, u.referrer_user_id)
        if ref is not None:
            referrer_brief = AdminUserBrief(
                id=ref.id, email=ref.email, username=ref.username
            )

    ref_rows = await session.execute(
        select(User)
        .where(User.referrer_user_id == user_id)
        .order_by(User.created_at.desc())
        .limit(100)
    )
    referrals = [
        AdminReferralInviteRow(
            id=r.id,
            email=r.email,
            username=r.username,
            created_at=r.created_at,
        )
        for r in ref_rows.scalars().all()
    ]

    ord_rows = await session.execute(
        select(Order)
        .where(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .limit(25)
    )
    orders = [
        AdminOrderBrief(
            id=o.id,
            status=o.status,
            brand_name=o.brand_name,
            price_cents=o.price_cents,
            created_at=o.created_at,
        )
        for o in ord_rows.scalars().all()
    ]

    rew = await session.execute(
        select(func.coalesce(func.sum(BalanceTransaction.amount_cents), 0)).where(
            BalanceTransaction.user_id == user_id,
            BalanceTransaction.type == BalanceTransactionType.referral_reward,
        )
    )
    referral_rewards_total = int(rew.scalar_one() or 0)

    return AdminUserDetail(
        id=u.id,
        email=u.email,
        username=u.username,
        created_at=u.created_at,
        is_active=u.is_active,
        is_admin=u.is_admin,
        is_email_verified=u.is_email_verified,
        balance_cents=u.balance_cents,
        referral_code=u.referral_code,
        referral_slug_locked=u.referral_slug_locked,
        referrer=referrer_brief,
        referrals=referrals,
        referral_rewards_total_cents=referral_rewards_total,
        orders=orders,
        last_seen_at=u.last_seen_at,
        last_device_kind=device_kind_from_user_agent(u.last_user_agent),
    )


@router.patch("/{user_id}", response_model=AdminUserRow)
async def patch_user(
    user_id: int,
    body: AdminUserPatchBody,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_current_admin),
) -> AdminUserRow:
    if user_id == admin.id and body.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя отключить собственную учётную запись",
        )

    u = await session.get(User, user_id)
    if u is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    u.is_active = body.is_active
    await session.flush()
    await session.refresh(u)

    oc = await session.execute(
        select(func.count(Order.id)).where(Order.user_id == u.id)
    )
    orders_total = int(oc.scalar_one() or 0)
    pc = await session.execute(
        select(func.count(Payment.id)).where(
            Payment.user_id == u.id,
            Payment.status == PaymentStatus.succeeded,
        )
    )
    payments_succeeded = int(pc.scalar_one() or 0)

    return AdminUserRow(
        id=u.id,
        email=u.email,
        username=u.username,
        created_at=u.created_at,
        is_active=u.is_active,
        is_admin=u.is_admin,
        orders_total=orders_total,
        payments_succeeded=payments_succeeded,
        last_seen_at=u.last_seen_at,
        last_device_kind=device_kind_from_user_agent(u.last_user_agent),
    )


@router.post(
    "/{user_id}/grant-credits",
    response_model=AdminGrantCreditsResponse,
)
async def grant_credits(
    user_id: int,
    body: AdminGrantCreditsBody,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_current_admin),
) -> AdminGrantCreditsResponse:
    try:
        bt, new_bal = await grant_credits_by_admin(
            session,
            target_user_id=user_id,
            amount_cents=body.amount_cents,
            admin_user_id=admin.id,
            reason=body.reason,
        )
    except AdminCreditsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    return AdminGrantCreditsResponse(
        transaction_id=bt.id,
        new_balance_cents=new_bal,
    )
