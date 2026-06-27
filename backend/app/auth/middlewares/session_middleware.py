from datetime import datetime, timezone

from redis.asyncio import Redis
from sqlalchemy import select
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import settings


class SessionValidationMiddleware(BaseHTTPMiddleware):
    """
    Validates the access token against the DB sessions table on every
    protected request. Enforces single-session-per-user: if a newer login
    revoked this session, the request is rejected immediately with 401.

    Redis is used as a short-lived cache (60 s) to avoid a DB hit on every
    request while still catching revocations within one minute.
    """

    _PUBLIC_PATHS = frozenset(
        {
            "/api/auth/login",
            "/api/auth/register",
            "/api/auth/forgot-password",
            "/api/auth/reset-password",
            "/api/auth/refresh",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
        }
    )
    _PUBLIC_PREFIXES = ("/api/auth/google", "/api/auth/azure")

    def _is_public(self, path: str) -> bool:
        return path in self._PUBLIC_PATHS or any(path.startswith(p) for p in self._PUBLIC_PREFIXES)

    def _extract_token(self, request: Request) -> str | None:
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

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if self._is_public(request.url.path):
            return await call_next(request)

        token = self._extract_token(request)
        if not token:
            return await call_next(request)  # no token → dependency raises 401

        from app.auth.utils import hash_token

        token_hash = hash_token(token)
        cache_key = f"session:{token_hash}"

        # ── Redis cache check ─────────────────────────────────────────────────
        try:
            redis = Redis.from_url(settings.redis_url)
            cached = await redis.get(cache_key)
            await redis.aclose()
            if cached == b"0":
                return self._unauthorized("Session has been revoked")
            if cached == b"1":
                return await call_next(request)
        except Exception:
            pass  # Redis unavailable — fall through to DB

        # ── DB session check ──────────────────────────────────────────────────
        try:
            from app.auth.models.session_models import Sessions
            from app.database import async_session_factory

            now = datetime.now(timezone.utc)
            async with async_session_factory() as db:
                result = await db.execute(
                    select(Sessions).where(
                        Sessions.access_token_hash == token_hash,
                        Sessions.revoked_at.is_(None),
                        Sessions.expires_at > now,
                    )
                )
                session = result.scalar_one_or_none()

            if not session:
                try:
                    redis = Redis.from_url(settings.redis_url)
                    await redis.setex(cache_key, 60, "0")
                    await redis.aclose()
                except Exception:
                    pass
                return self._unauthorized("Session expired or revoked")

            ttl = min(60, max(1, int((session.expires_at - now).total_seconds())))
            try:
                redis = Redis.from_url(settings.redis_url)
                await redis.setex(cache_key, ttl, "1")
                await redis.aclose()
            except Exception:
                pass

        except Exception:
            pass  # DB unavailable — allow through (graceful degradation)

        return await call_next(request)
