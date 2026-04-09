"""Реферальная программа: ссылка, смена slug, статистика."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.dependencies import get_current_user
from app.models.balance_transaction import BalanceTransaction
from app.models.enums import BalanceTransactionType
from app.models.user import User
from app.schemas.referral import ReferralCodeUpdateBody, ReferralSummaryResponse
from app.services.referrals import (
    assign_unique_referral_code,
    validate_custom_referral_slug,
)

logger = logging.getLogger(__name__)

router = APIRouter()


async def _build_summary(session: AsyncSession, user: User) -> ReferralSummaryResponse:
    await assign_unique_referral_code(session, user)

    ref_count = await session.scalar(
        select(func.count()).select_from(User).where(User.referrer_user_id == user.id)
    )
    rewards_sum = await session.scalar(
        select(func.coalesce(func.sum(BalanceTransaction.amount_cents), 0)).where(
            BalanceTransaction.user_id == user.id,
            BalanceTransaction.type == BalanceTransactionType.referral_reward,
        )
    )

    code = user.referral_code or ""
    return ReferralSummaryResponse(
        referral_code=code,
        referral_link_query=f"?ref={code}" if code else "?ref=",
        slug_locked=user.referral_slug_locked,
        referrals_count=int(ref_count or 0),
        rewards_total_cents=int(rewards_sum or 0),
    )


@router.get("/summary", response_model=ReferralSummaryResponse)
async def referral_summary(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> ReferralSummaryResponse:
    return await _build_summary(session, user)


@router.patch("/code", response_model=ReferralSummaryResponse)
async def referral_set_custom_code(
    body: ReferralCodeUpdateBody,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> ReferralSummaryResponse:
    await assign_unique_referral_code(session, user)

    if user.referral_slug_locked:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Кастомный код уже зафиксирован. Изменить нельзя.",
        )

    err = validate_custom_referral_slug(body.code)
    if err:
        raise HTTPException(status_code=400, detail=err)

    new_code = body.code.strip().lower()
    if new_code == user.referral_code:
        user.referral_slug_locked = True
        await session.flush()
        return await _build_summary(session, user)

    taken = await session.scalar(select(User.id).where(User.referral_code == new_code))
    if taken is not None and taken != user.id:
        raise HTTPException(status_code=409, detail="Такой код уже занят.")

    user.referral_code = new_code
    user.referral_slug_locked = True
    try:
        await session.flush()
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Такой код уже занят.") from None

    logger.info("referral slug customized user_id=%s code=%s", user.id, new_code)
    return await _build_summary(session, user)
