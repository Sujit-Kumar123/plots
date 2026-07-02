import uuid
from dataclasses import dataclass
from typing import Callable

from fastapi import Depends, Header

from app.common.exceptions import ForbiddenException, UnauthorizedException


@dataclass
class CurrentUser:
    user_id: uuid.UUID
    role: str
    email: str


async def get_current_user(
    x_user_id: str = Header(..., alias="x-user-id"),
    x_user_role: str = Header(default="user", alias="x-user-role"),
    x_user_email: str = Header(default="", alias="x-user-email"),
) -> CurrentUser:
    try:
        return CurrentUser(
            user_id=uuid.UUID(x_user_id),
            role=x_user_role,
            email=x_user_email,
        )
    except (ValueError, TypeError):
        raise UnauthorizedException("Invalid user identity headers")


def require_role(allowed_roles: list[str]) -> Callable:
    async def checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise ForbiddenException("Insufficient role")
        return current_user
    return checker
