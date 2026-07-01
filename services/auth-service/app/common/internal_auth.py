from fastapi import Header, HTTPException, status

from app.config import settings


async def require_internal_secret(
    x_internal_secret: str | None = Header(None, alias="x-internal-secret"),
) -> None:
    """FastAPI dependency for internal-only endpoints called by the api-gateway."""
    if not settings.internal_service_secret:
        return  # disabled when secret not configured (local dev without secret)
    if x_internal_secret != settings.internal_service_secret:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
