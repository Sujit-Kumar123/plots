from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.schemas import ValidateSessionRequest
from app.auth.models.session_models import Sessions
from app.common.internal_auth import require_internal_secret
from app.database import get_db

internal_router = APIRouter(prefix="/api/auth/internal", tags=["internal"])


@internal_router.post("/validate-session")
async def validate_session(
    body: ValidateSessionRequest,
    _: None = Depends(require_internal_secret),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(Sessions).where(
            Sessions.access_token_hash == body.token_hash,
            Sessions.revoked_at.is_(None),
            Sessions.expires_at > now,
        )
    )
    session = result.scalar_one_or_none()
    return {"valid": session is not None}
