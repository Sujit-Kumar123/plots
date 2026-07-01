"""Catch-all proxy routes for backend microservices.

Each router is mounted at its canonical path prefix in main.py.
request.url.path is forwarded unchanged so downstream services receive
the exact path the client sent (no prefix stripping or rewriting needed).
"""

from fastapi import APIRouter, Request
from fastapi.responses import Response

from app.config import settings
from app.proxy import proxy

# ── Helpers ──────────────────────────────────────────────────────────────────

def _make_router(*tags: str) -> APIRouter:
    return APIRouter(tags=list(tags))


def _sub(base_url_attr: str):
    """Factory: returns a route handler that proxies to settings.<base_url_attr>."""
    async def handler(path: str, request: Request) -> Response:
        return await proxy(request, getattr(settings, base_url_attr), request.url.path)
    return handler


def _root(base_url_attr: str):
    async def handler(request: Request) -> Response:
        return await proxy(request, getattr(settings, base_url_attr), request.url.path)
    return handler


_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]


def _make_proxy_router(base_url_attr: str, *tags: str) -> APIRouter:
    router = _make_router(*tags)

    @router.api_route("/{path:path}", methods=_METHODS)
    async def proxy_sub(path: str, request: Request) -> Response:
        return await proxy(request, getattr(settings, base_url_attr), request.url.path)

    @router.api_route("", methods=_METHODS)
    async def proxy_root(request: Request) -> Response:
        return await proxy(request, getattr(settings, base_url_attr), request.url.path)

    return router


# ── Auth service: /api/auth  /api/profile  /api/admin  /api/uploads ──────────
# All four path prefixes point to the single auth-service container.

auth_router = _make_proxy_router("auth_service_url", "auth")
profile_router = _make_proxy_router("auth_service_url", "profile")
admin_router = _make_proxy_router("auth_service_url", "admin")
uploads_router = _make_proxy_router("auth_service_url", "uploads")

# ── Payment service: /api/payments ───────────────────────────────────────────

payment_router = _make_proxy_router("payment_service_url", "payments")

# ── Notification service: /api/notifications ─────────────────────────────────

notification_router = _make_proxy_router("notification_service_url", "notifications")
