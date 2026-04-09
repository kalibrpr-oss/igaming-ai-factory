from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.user import User
from app.services.auth.jwt_tokens import decode_token
from app.services.user_activity import touch_user_activity_if_due

security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_session),
    creds: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    sub = decode_token(creds.credentials)
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
        )
    try:
        user_id = int(sub)
    except ValueError:
        raise HTTPException(status_code=401, detail="Недействительный токен")
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    await touch_user_activity_if_due(
        session, user, request.headers.get("user-agent")
    )
    return user


async def get_current_user_optional(
    session: AsyncSession = Depends(get_session),
    creds: HTTPAuthorizationCredentials | None = Depends(optional_security),
) -> User | None:
    """Для эндпоинтов вроде превью цены: с JWT — персональная скидка, без — базовая цена."""
    if creds is None or not creds.credentials:
        return None
    sub = decode_token(creds.credentials)
    if sub is None:
        return None
    try:
        user_id = int(sub)
    except ValueError:
        return None
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        return None
    return user


async def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Нужны права администратора")
    return user
