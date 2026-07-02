"""Proxy routes for backend microservices.

Each router is mounted at its canonical path prefix in main.py.
``request.url.path`` is forwarded unchanged so downstream services receive
the exact path the client sent (no prefix stripping or rewriting needed).

Authorization is enforced at the route level:
- GET    → read permission
- POST / PUT / PATCH → write permission
- DELETE → delete permission

Routes that need no special permission (auth, payments) use the open router.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response

from app.common.dependencies import require_permission
from app.config import settings
from app.proxy import proxy

_ALL_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
_READ    = ["GET"]
_WRITE   = ["POST", "PUT", "PATCH"]
_DELETE  = ["DELETE"]


# ---------------------------------------------------------------------------
# Router factories
# ---------------------------------------------------------------------------

def _make_open_router(*tags: str, base_url_attr: str) -> APIRouter:
    """No permission gate — the auth middleware ensures a valid token."""
    router = APIRouter(tags=list(tags))
    bua = base_url_attr

    async def _root(request: Request) -> Response:
        return await proxy(request, getattr(settings, bua), request.url.path)

    async def _sub(path: str, request: Request) -> Response:
        return await proxy(request, getattr(settings, bua), request.url.path)

    router.add_api_route("", _root, methods=_ALL_METHODS)
    router.add_api_route("/{path:path}", _sub, methods=_ALL_METHODS)
    return router


def _make_rwd_router(
    base_url_attr: str,
    read_perm: str,
    write_perm: str,
    delete_perm: str,
    service_name: str,
    *tags: str,
) -> APIRouter:
    """Read / Write / Delete proxy router with per-method permission guards.

    Operation IDs are made unique by embedding *service_name* so OpenAPI does
    not emit duplicate-operation-ID warnings.
    """
    router = APIRouter(tags=list(tags))
    bua = base_url_attr

    # ── read ─────────────────────────────────────────────────────────────────
    async def _read_root(request: Request) -> Response:
        return await proxy(request, getattr(settings, bua), request.url.path)
    _read_root.__name__ = f"{service_name}_read_root"

    async def _read_sub(path: str, request: Request) -> Response:
        return await proxy(request, getattr(settings, bua), request.url.path)
    _read_sub.__name__ = f"{service_name}_read_sub"

    # ── write ─────────────────────────────────────────────────────────────────
    async def _write_root(request: Request) -> Response:
        return await proxy(request, getattr(settings, bua), request.url.path)
    _write_root.__name__ = f"{service_name}_write_root"

    async def _write_sub(path: str, request: Request) -> Response:
        return await proxy(request, getattr(settings, bua), request.url.path)
    _write_sub.__name__ = f"{service_name}_write_sub"

    # ── delete ────────────────────────────────────────────────────────────────
    async def _delete_sub(path: str, request: Request) -> Response:
        return await proxy(request, getattr(settings, bua), request.url.path)
    _delete_sub.__name__ = f"{service_name}_delete_sub"

    _rd = [Depends(require_permission(read_perm))]
    _wd = [Depends(require_permission(write_perm))]
    _dd = [Depends(require_permission(delete_perm))]

    router.add_api_route("",            _read_root,  methods=_READ,   dependencies=_rd)
    router.add_api_route("/{path:path}", _read_sub,   methods=_READ,   dependencies=_rd)
    router.add_api_route("",            _write_root, methods=_WRITE,  dependencies=_wd)
    router.add_api_route("/{path:path}", _write_sub,  methods=_WRITE,  dependencies=_wd)
    router.add_api_route("/{path:path}", _delete_sub, methods=_DELETE, dependencies=_dd)

    return router


# ---------------------------------------------------------------------------
# Auth service — /api/auth  /api/auth/roles  /api/auth/permissions
#                /api/profile  /api/admin  /api/uploads
# All point to the single auth-service container.
# ---------------------------------------------------------------------------

# Pure auth routes: login, register, refresh, OAuth flows.
# Public paths are already exempted by the middleware.  Protected auth routes
# (logout, change-password) just need a valid token — no special permission.
auth_router = _make_open_router("auth", base_url_attr="auth_service_url")

# Role management — mounted at /api/auth/roles (registered before auth_router
# in main.py so FastAPI matches it first)
roles_proxy_router = _make_rwd_router(
    "auth_service_url", "roles:read", "roles:write", "roles:delete",
    "roles_proxy", "roles",
)

# Permission management — mounted at /api/auth/permissions
permissions_proxy_router = _make_rwd_router(
    "auth_service_url", "permissions:read", "permissions:write", "permissions:delete",
    "permissions_proxy", "permissions",
)

# Profile management — mounted at /api/profile
profile_router = _make_rwd_router(
    "auth_service_url", "profile:read", "profile:write", "profile:write",
    "profile", "profile",
)

# User management — mounted at /api/admin (alongside the local audit router)
admin_router = _make_rwd_router(
    "auth_service_url", "users:read", "users:write", "users:delete",
    "admin", "admin",
)

# File uploads — mounted at /api/uploads
uploads_router = _make_rwd_router(
    "auth_service_url", "uploads:read", "uploads:write", "uploads:delete",
    "uploads", "uploads",
)

# ---------------------------------------------------------------------------
# Payment service — /api/payments
# Any authenticated user may access their own payments.
# ---------------------------------------------------------------------------

payment_router = _make_open_router("payments", base_url_attr="payment_service_url")

# ---------------------------------------------------------------------------
# Notification service — /api/notifications
# Sending notifications requires notifications:write.
# ---------------------------------------------------------------------------

notification_router = _make_rwd_router(
    "notification_service_url",
    "notifications:write", "notifications:write", "notifications:write",
    "notifications", "notifications",
)
