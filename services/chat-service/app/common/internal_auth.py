from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings

_SKIP = frozenset({"/health", "/health/ready"})


class InternalAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in _SKIP:
            return await call_next(request)
        if not settings.internal_service_secret:
            return await call_next(request)
        secret = request.headers.get("x-internal-secret")
        if not secret or secret != settings.internal_service_secret:
            return JSONResponse(status_code=403, content={"detail": "Forbidden"})
        return await call_next(request)
