from collections.abc import Callable

from fastapi import HTTPException, Request, status


def require_permission(permission: str) -> Callable:
    """Requires the user to hold *permission* (e.g. ``"users:read"``).

    Supports wildcard: a superadmin whose permissions contain ``"*"`` bypasses
    every check.  Permissions are fetched from auth-service and cached in Redis
    by ``SessionValidationMiddleware`` into ``request.state.user_permissions``.
    """

    async def checker(request: Request) -> None:
        perms: frozenset[str] = getattr(request.state, "user_permissions", frozenset())
        if "*" in perms:
            return
        resource, _, action = permission.partition(":")
        if (
            permission not in perms
            and f"{resource}:*" not in perms
            and f"*:{action}" not in perms
            and "*:*" not in perms
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {permission}",
            )

    return checker


def require_permissions(permissions: list[str]) -> Callable:
    """Requires the user to hold ALL listed permission codes."""

    async def checker(request: Request) -> None:
        perms: frozenset[str] = getattr(request.state, "user_permissions", frozenset())
        if "*" in perms:
            return
        for permission in permissions:
            resource, _, action = permission.partition(":")
            if (
                permission not in perms
                and f"{resource}:*" not in perms
                and f"*:{action}" not in perms
                and "*:*" not in perms
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing permission: {permission}",
                )

    return checker


def require_role(allowed_roles: list[str]) -> Callable:
    """Requires the user's role to be one of *allowed_roles*."""

    async def checker(request: Request) -> None:
        role: str = getattr(request.state, "user_role", "")
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' is not allowed. Required: {allowed_roles}",
            )

    return checker
