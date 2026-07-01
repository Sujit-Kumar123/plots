import structlog
from redis.asyncio import ConnectionPool, Redis
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import settings

logger = structlog.get_logger()

_SKIP_PATHS = frozenset({"/health", "/health/ready", "/docs", "/redoc", "/openapi.json"})

# Endpoint-specific limits applied on top of the global per-IP limit
_ENDPOINT_LIMITS: dict[str, str] = {
    "/api/auth/login": "rate_limit_login",
    "/api/auth/register": "rate_limit_register",
    "/api/auth/forgot-password": "rate_limit_password_reset",
}

_PERIOD_SECONDS: dict[str, int] = {
    "second": 1,
    "minute": 60,
    "hour": 3600,
    "day": 86400,
}

# Module-level connection pool — created once, reused across all requests
_pool: ConnectionPool | None = None


def _get_redis() -> Redis:
    global _pool
    if _pool is None:
        _pool = ConnectionPool.from_url(settings.redis_url, decode_responses=False, max_connections=20)
    return Redis(connection_pool=_pool)


def _parse_rate(rate_str: str) -> tuple[int, int]:
    """'300/minute' → (300, 60)."""
    count, period = rate_str.split("/")
    return int(count), _PERIOD_SECONDS.get(period, 60)


def _too_many(ttl: int) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "data": None,
            "message": "Too many requests. Please try again later.",
            "errors": None,
        },
        headers={"Retry-After": str(ttl)},
    )


async def _check_limit(redis: Redis, key: str, max_req: int, window: int) -> int | None:
    """Returns TTL seconds if limit exceeded, None if allowed."""
    current = await redis.incr(key)
    if current == 1:
        await redis.expire(key, window)
    if current > max_req:
        return max(await redis.ttl(key), 1)
    return None


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Two-tier Redis rate limiter (all traffic is at the gateway, so one middleware covers everything):
      1. Global limit — every /api/* path, per client IP
      2. Endpoint limit — stricter limits for sensitive auth paths

    Degrades gracefully when Redis is unavailable (requests are allowed through).
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path

        if path in _SKIP_PATHS or not path.startswith("/api/"):
            return await call_next(request)

        # Prefer forwarded IP so SSR calls (127.0.0.1 from Next.js) bucket by real browser IP
        client_ip = (
            request.headers.get("x-real-ip")
            or request.headers.get("x-forwarded-for", "").split(",")[0].strip()
            or (request.client.host if request.client else "unknown")
        )

        try:
            redis = _get_redis()

            # ── 1. Global per-IP limit ─────────────────────────────────────────
            global_max, global_window = _parse_rate(settings.rate_limit_api)
            ttl = await _check_limit(redis, f"rl:global:{client_ip}", global_max, global_window)
            if ttl is not None:
                await logger.awarning("rate_limit_exceeded", tier="global", path=path, client_ip=client_ip)
                return _too_many(ttl)

            # ── 2. Endpoint-specific stricter limit ────────────────────────────
            config_attr = _ENDPOINT_LIMITS.get(path)
            if config_attr:
                ep_max, ep_window = _parse_rate(getattr(settings, config_attr, "10/minute"))
                ttl = await _check_limit(redis, f"rl:endpoint:{path}:{client_ip}", ep_max, ep_window)
                if ttl is not None:
                    await logger.awarning("rate_limit_exceeded", tier="endpoint", path=path, client_ip=client_ip)
                    return _too_many(ttl)

        except Exception:
            pass  # Redis unavailable — never block requests

        return await call_next(request)
