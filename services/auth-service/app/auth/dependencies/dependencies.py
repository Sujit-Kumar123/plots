import uuid

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.common.exceptions import UnauthorizedException
from app.database import get_db


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    user_id_header = request.headers.get("x-user-id")
    if not user_id_header:
        raise UnauthorizedException()

    try:
        user_uuid = uuid.UUID(user_id_header)
    except ValueError:
        raise UnauthorizedException()

    result = await db.execute(
        select(User).where(User.id == user_uuid, User.is_deleted == False)  # noqa: E712
    )
    user = result.scalar_one_or_none()

    if not user:
        raise UnauthorizedException()
    if not user.is_active:
        raise UnauthorizedException("Account is deactivated")

    return user
