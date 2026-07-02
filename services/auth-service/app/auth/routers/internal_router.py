from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models.permission_models import Permissions, RolePermissions
from app.auth.models.role_models import Roles
from app.auth.models.session_models import Sessions
from app.common.internal_auth import require_internal_secret
from app.database import get_db

internal_router = APIRouter(prefix="/api/auth/internal", tags=["internal"])


class ValidateSessionRequest(BaseModel):
    token_hash: str


class RolePermissionsRequest(BaseModel):
    role_name: str


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


@internal_router.post("/role-permissions")
async def get_role_permissions(
    body: RolePermissionsRequest,
    _: None = Depends(require_internal_secret),
    db: AsyncSession = Depends(get_db),
):
    """Return the permission codes assigned to a role (used by the api-gateway permission cache)."""
    result = await db.execute(
        select(Permissions.code)
        .join(RolePermissions, RolePermissions.permission_id == Permissions.id)
        .join(Roles, Roles.id == RolePermissions.role_id)
        .where(Roles.name == body.role_name)
    )
    codes = [row[0] for row in result.fetchall()]
    return {"permissions": codes}
