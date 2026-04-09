"""
Пополнение кошелька: mock (dev) и ЮKassa (прод / тестовый магазин).
"""

from __future__ import annotations

import asyncio
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from yookassa.domain.exceptions.unauthorized_error import UnauthorizedError

from app.config import settings
from app.db.session import get_session
from app.dependencies import get_current_user
from app.models.enums import PaymentKind, PaymentProvider, PaymentStatus
from app.models.payment import Payment
from app.models.user import User
from app.schemas.wallet import (
    UserMockTopupBody,
    UserMockTopupResponse,
    YooKassaStatusResponse,
    YooKassaTopupCreateBody,
    YooKassaTopupCreatedResponse,
)
from app.services.payments.settlement import SettlementError, apply_payment_succeeded
from app.services.payments.yookassa_service import (
    sync_create_wallet_topup_payment,
    sync_fetch_payment,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/yookassa/status",
    response_model=YooKassaStatusResponse,
    summary="Доступность пополнения через ЮKassa",
)
async def yookassa_status() -> YooKassaStatusResponse:
    ok = bool(settings.yookassa_shop_id.strip() and settings.yookassa_secret_key.strip())
    return YooKassaStatusResponse(yookassa_topup_available=ok)


@router.post(
    "/yookassa/create",
    response_model=YooKassaTopupCreatedResponse,
    summary="Создать платёж ЮKassa и получить ссылку на оплату",
)
async def yookassa_create_topup(
    body: YooKassaTopupCreateBody,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> YooKassaTopupCreatedResponse:
    if not settings.yookassa_shop_id.strip() or not settings.yookassa_secret_key.strip():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Пополнение картой временно недоступно",
        )

    return_url = f"{settings.public_app_url.rstrip('/')}/dashboard?topup=yookassa"

    payment = Payment(
        user_id=user.id,
        order_id=None,
        kind=PaymentKind.wallet_topup,
        provider=PaymentProvider.yoomoney,
        external_id=None,
        amount_cents=body.amount_cents,
        status=PaymentStatus.pending,
    )
    session.add(payment)
    await session.flush()

    try:
        yid, confirmation_url = await asyncio.to_thread(
            sync_create_wallet_topup_payment,
            amount_cents=body.amount_cents,
            return_url=return_url,
            internal_payment_id=payment.id,
            user_id=user.id,
        )
    except UnauthorizedError:
        logger.warning("ЮKassa: неверные shopId / secret_key")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "ЮKassa отклонила ключи: проверь YOOKASSA_SHOP_ID и YOOKASSA_SECRET_KEY "
                "в backend/.env (один магазин = одна пара; тестовый секрет только к тестовому shopId). "
                "Перевыпусти секрет в кабинете и перезапусти сервер."
            ),
        ) from None
    except Exception as exc:
        logger.exception("ЮKassa: не удалось создать платёж")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Не удалось создать платёж. Попробуйте позже.",
        ) from exc

    payment.external_id = yid
    await session.flush()

    return YooKassaTopupCreatedResponse(
        payment_id=payment.id,
        confirmation_url=confirmation_url,
    )


@router.post("/yookassa/webhook")
async def yookassa_webhook(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    """
    Уведомления ЮKassa. Дубли игнорируются за счёт идемпотентности зачисления.
    Проверяем статус платежа через API, затем зачисляем.
    """
    if not settings.yookassa_shop_id.strip() or not settings.yookassa_secret_key.strip():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON") from exc

    event = payload.get("event") or ""
    obj = payload.get("object") or {}
    if event != "payment.succeeded":
        return {"status": "ignored"}

    yid = obj.get("id")
    if not yid:
        return {"status": "no_id"}

    try:
        remote = await asyncio.to_thread(sync_fetch_payment, str(yid))
    except Exception:
        logger.exception("ЮKassa: не удалось запросить платёж %s", yid)
        raise HTTPException(status_code=502, detail="YooKassa API error") from None

    remote_status = getattr(remote, "status", None)
    if remote_status != "succeeded":
        return {"status": "not_succeeded"}

    result = await session.execute(
        select(Payment).where(
            Payment.external_id == str(yid),
            Payment.kind == PaymentKind.wallet_topup,
        )
    )
    payment = result.scalar_one_or_none()
    if payment is None:
        logger.warning("yookassa webhook: нет локального платежа external_id=%s", yid)
        return {"status": "unknown_payment"}

    try:
        await apply_payment_succeeded(
            session,
            payment.id,
            raw_payload={"source": "yookassa_webhook", "event": payload},
        )
    except SettlementError as e:
        if payment.status == PaymentStatus.succeeded:
            return {"status": "already_done"}
        logger.warning("yookassa webhook settlement: %s", e)
        raise HTTPException(status_code=409, detail=str(e)) from e

    return {"status": "ok"}


@router.post(
    "/mock-topup",
    response_model=UserMockTopupResponse,
    summary="Тестовое пополнение баланса (mock)",
)
async def user_mock_topup(
    body: UserMockTopupBody,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> UserMockTopupResponse:
    """
    Создаёт платёж wallet_topup (mock) и сразу зачисляет через apply_payment_succeeded.
    Доступно только если enable_user_wallet_mock_topup=true (никогда на проде).
    """
    if not settings.enable_user_wallet_mock_topup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found",
        )

    payment = Payment(
        user_id=user.id,
        order_id=None,
        kind=PaymentKind.wallet_topup,
        provider=PaymentProvider.mock,
        external_id=f"user-mock-{uuid.uuid4()}",
        amount_cents=body.amount_cents,
        status=PaymentStatus.pending,
    )
    session.add(payment)
    await session.flush()

    try:
        await apply_payment_succeeded(
            session,
            payment.id,
            raw_payload={"source": "user_wallet_mock"},
        )
    except SettlementError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e

    bal = await session.scalar(select(User.balance_cents).where(User.id == user.id))
    return UserMockTopupResponse(
        payment_id=payment.id,
        user_balance_cents=int(bal or 0),
    )
