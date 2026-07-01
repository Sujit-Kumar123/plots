from fastapi import Header, HTTPException, status

from app.config import settings


async def require_internal_auth(
    x_internal_secret: str = Header(..., alias="x-internal-secret"),
) -> None:
    if settings.internal_service_secret and x_internal_secret != settings.internal_service_secret:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
