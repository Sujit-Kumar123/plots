import uuid
from typing import Callable

from fastapi import Cookie, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.utils import decode_token
from app.common.exceptions import ForbiddenException, UnauthorizedException
from app.database import get_db

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    access_token: str | None = Cookie(None, include_in_schema=False),
    db: AsyncSession = Depends(get_db),
) -> User:
    token: str | None = None
    if credentials:
        token = credentials.credentials
    elif access_token:
        token = access_token

    if not token:
        raise UnauthorizedException()
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise UnauthorizedException()

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException()

    result = await db.execute(
        select(User).where(User.id == uuid.UUID(user_id), User.is_deleted == False)  # noqa: E712
    )
    user = result.scalar_one_or_none()

    if not user:
        raise UnauthorizedException()
    if not user.is_active:
        raise UnauthorizedException("Account is deactivated")

    return user


# ── Permission helpers ────────────────────────────────────────────────────────


def _get_user_permission_codes(user: User) -> list[str]:
    if not user.role:
        return []
    return [rp.permission.code for rp in user.role.role_permissions]


def _check_permission(codes: list[str], required: str) -> bool:
    """Supports wildcard matching: *:*, resource:*, *:action."""
    if "*:*" in codes:
        return True
    resource, _, action = required.partition(":")
    return required in codes or f"{resource}:*" in codes or f"*:{action}" in codes


# ── Dependency factories ──────────────────────────────────────────────────────


def require_permission(permission: str) -> Callable:
    """Requires the user to have a specific permission code (e.g. 'users:read')."""

    async def checker(current_user: User = Depends(get_current_user)) -> User:
        codes = _get_user_permission_codes(current_user)
        if not _check_permission(codes, permission):
            raise ForbiddenException(f"Missing permission: {permission}")
        return current_user

    return checker


def require_permissions(permissions: list[str]) -> Callable:
    """Requires the user to hold ALL listed permission codes."""

    async def checker(current_user: User = Depends(get_current_user)) -> User:
        codes = _get_user_permission_codes(current_user)
        for perm in permissions:
            if not _check_permission(codes, perm):
                raise ForbiddenException(f"Missing permission: {perm}")
        return current_user

    return checker


def require_role(allowed_roles: list[str]) -> Callable:
    """Role-based guard (kept for backward compatibility)."""

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.role or current_user.role.short_name not in allowed_roles:
            raise ForbiddenException("Insufficient permissions")
        return current_user

    return role_checker
