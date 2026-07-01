import asyncio
import logging
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.audit.service import log_action

logger = logging.getLogger(__name__)

_AUDIT_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})
_SKIP_AUDIT_PREFIXES = (
    "/api/auth/login",
    "/api/auth/register",
    "/api/auth/refresh",
    "/api/auth/internal/",
    "/health",
)


def _resource_type_from_path(path: str) -> str:
    parts = [p for p in path.strip("/").split("/") if p and not _is_uuid_like(p)]
    return parts[-1] if parts else "unknown"


def _is_uuid_like(segment: str) -> bool:
    try:
        uuid.UUID(segment)
        return True
    except ValueError:
        return segment.isdigit() or len(segment) > 30


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)

        if request.method not in _AUDIT_METHODS:
            return response
        if response.status_code >= 500:
            return response
        if any(request.url.path.startswith(p) for p in _SKIP_AUDIT_PREFIXES):
            return response

        user_id: uuid.UUID | None = None
        raw_id = getattr(request.state, "user_id", None)
        if raw_id:
            try:
                user_id = uuid.UUID(raw_id)
            except (ValueError, TypeError):
                pass

        asyncio.ensure_future(
            log_action(
                user_id=user_id,
                action=f"{request.method.lower()}:{request.url.path}",
                resource_type=_resource_type_from_path(request.url.path),
                ip_address=request.client.host if request.client else None,
            )
        )

        return response
