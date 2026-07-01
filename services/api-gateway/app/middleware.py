from hashlib import sha256

import httpx
from jose import JWTError, jwt
from redis.asyncio import Redis
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import settings

# Paths that never require a token (login, register, OAuth redirects, etc.)
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


class SessionValidationMiddleware(BaseHTTPMiddleware):
    """
    Single auth middleware for the gateway.

    1. Skips truly public paths (login, register, OAuth, health, internal).
    2. If a token is present, validates it via Redis cache → auth-service HTTP fallback.
    3. Decodes the JWT and populates request.state.user_id / user_payload so downstream
       handlers and AuditMiddleware can use them.
    4. CQRS routes (/api/v1/*) require a token; backend proxy routes do not.
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
    def _unauthorized(message: str) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={"success": False, "data": None, "message": message, "errors": None},
        )

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

            # Cache the result in Redis so subsequent requests hit the fast path
            try:
                ttl = 60
                redis = Redis.from_url(settings.redis_url, decode_responses=False)
                await redis.setex(cache_key, ttl, "1" if valid else "0")
                await redis.aclose()
            except Exception:
                pass

            return valid
        except Exception:
            # auth-service unavailable — allow through (graceful degradation)
            return True

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
            request.state.user_id = payload.get("sub")
            request.state.user_payload = payload
        except JWTError:
            return self._unauthorized("Invalid token")

        return await call_next(request)
