from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.user import User
from app.services.auth.jwt_tokens import decode_token

security = HTTPBearer()


async def get_current_user(
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
    return user


async def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Нужны права администратора")
    return user
