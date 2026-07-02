import json
from hashlib import sha256

import httpx
from jose import JWTError, jwt
from redis.asyncio import Redis
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.common.responses import ResponseHandler
from app.config import settings

# ---------------------------------------------------------------------------
# Public / protected path sets
# ---------------------------------------------------------------------------

_PUBLIC_PATHS = frozenset(
    {
        "/api/auth/login",
        "/api/auth/register",
        "/api/auth/forgot-password",
        "/api/auth/reset-password",
        "/api/auth/refresh",
        "/health",
        "/health/ready",
        "/docs",
        "/redoc",
        "/openapi.json",
    }
)
_PUBLIC_PREFIXES = ("/api/auth/google", "/api/auth/azure", "/api/auth/internal/")

# CQRS routes must have a valid token — 401 if missing
_REQUIRE_AUTH_PREFIXES = ("/api/v1/",)

# How long (seconds) role-permission sets are cached in Redis.
_PERM_CACHE_TTL = 300  # 5 minutes


async def _fetch_role_permissions(http_client: httpx.AsyncClient, role_name: str) -> frozenset[str]:
    """
    Return the permission codes for *role_name*.

    Fast path: Redis cache keyed by ``perms:{role_name}`` with a 5-minute TTL.
    Slow path: POST to auth-service ``/api/auth/internal/role-permissions``.
    If both are unavailable the empty set is returned so the request is rejected
    rather than granted phantom access.

    ``superadmin`` is always resolved locally — it never needs a DB round-trip.
    """
    if role_name == "superadmin":
        return frozenset({"*"})

    cache_key = f"perms:{role_name}"

    # ── Redis cache ───────────────────────────────────────────────────────────
    try:
        redis = Redis.from_url(settings.redis_url, decode_responses=True)
        cached = await redis.get(cache_key)
        await redis.aclose()
        if cached:
            return frozenset(json.loads(cached))
    except Exception:
        pass

    # ── auth-service lookup ───────────────────────────────────────────────────
    try:
        resp = await http_client.post(
            f"{settings.auth_service_url}/api/auth/internal/role-permissions",
            json={"role_name": role_name},
            headers={"x-internal-secret": settings.internal_service_secret},
            timeout=3.0,
        )
        if resp.status_code == 200:
            codes: list[str] = resp.json().get("permissions", [])
            try:
                redis = Redis.from_url(settings.redis_url, decode_responses=True)
                await redis.setex(cache_key, _PERM_CACHE_TTL, json.dumps(codes))
                await redis.aclose()
            except Exception:
                pass
            return frozenset(codes)
    except Exception:
        pass

    return frozenset()  # deny on failure — safer than granting unknown permissions


class SessionValidationMiddleware(BaseHTTPMiddleware):
    """
    Auth middleware for the gateway.

    1. Skips truly public paths (login, register, OAuth, health, internal).
    2. Validates the token via Redis cache → auth-service HTTP fallback.
    3. Decodes the JWT; populates request.state.user_id / user_payload / user_role /
       user_permissions (frozenset of permission codes fetched from auth-service and
       cached in Redis — never hardcoded here).
    4. CQRS routes (/api/v1/*) require a token; other backend proxy routes do not.

    Authorization (permission checks) is enforced at the router level via
    ``require_permission`` / ``require_permissions`` / ``require_role`` dependencies
    in ``app/common/dependencies.py``.
    """

    def _is_public(self, path: str) -> bool:
        return path in _PUBLIC_PATHS or any(path.startswith(p) for p in _PUBLIC_PREFIXES)

    @staticmethod
    def _extract_token(request: Request) -> str | None:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            return auth[7:]
        return request.cookies.get("access_token")

    @staticmethod
    def _unauthorized(message: str) -> Response:
        return ResponseHandler.unauthorized(message)

    @staticmethod
    def _hash_token(token: str) -> str:
        return sha256(token.encode()).hexdigest()

    async def _validate_session(self, request: Request, token: str) -> bool:
        """Returns True if the session is valid, False if revoked/expired."""
        token_hash = self._hash_token(token)
        cache_key = f"session:{token_hash}"

        # ── Redis cache check ─────────────────────────────────────────────────
        try:
            redis = Redis.from_url(settings.redis_url, decode_responses=False)
            cached = await redis.get(cache_key)
            await redis.aclose()
            if cached == b"0":
                return False
            if cached == b"1":
                return True
        except Exception:
            pass  # Redis unavailable — fall through to auth-service

        # ── auth-service HTTP check ───────────────────────────────────────────
        try:
            http_client: httpx.AsyncClient = request.app.state.http_client
            resp = await http_client.post(
                f"{settings.auth_service_url}/api/auth/internal/validate-session",
                json={"token_hash": token_hash},
                headers={"x-internal-secret": settings.internal_service_secret},
                timeout=3.0,
            )
            valid: bool = resp.status_code == 200 and resp.json().get("valid", False)

            try:
                redis = Redis.from_url(settings.redis_url, decode_responses=False)
                await redis.setex(cache_key, 60, "1" if valid else "0")
                await redis.aclose()
            except Exception:
                pass

            return valid
        except Exception:
            return True  # auth-service unavailable — allow through (graceful degradation)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path

        if self._is_public(path):
            return await call_next(request)

        token = self._extract_token(request)

        if not token:
            if any(path.startswith(p) for p in _REQUIRE_AUTH_PREFIXES):
                return self._unauthorized("Missing auth token")
            return await call_next(request)

        if not await self._validate_session(request, token):
            return self._unauthorized("Session expired or revoked")

        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        except JWTError:
            return self._unauthorized("Invalid token")

        request.state.user_id = payload.get("sub")
        request.state.user_payload = payload

        role: str = payload.get("role", "user")
        request.state.user_role = role  # consumed by AuditMiddleware

        http_client: httpx.AsyncClient = request.app.state.http_client
        user_permissions = await _fetch_role_permissions(http_client, role)
        request.state.user_permissions = user_permissions  # consumed by require_permission()

        return await call_next(request)
