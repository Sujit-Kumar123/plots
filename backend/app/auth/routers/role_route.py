import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_permission
from app.auth.models import User
from app.auth.schemas import (
    CreateRoleRequest,
    RoleWithPermissionsResponse,
    UpdateRoleRequest,
    UserWithProfileResponse,
)
from app.auth.service import RoleService
from app.common.responses import success_response
from app.database import get_db

router = APIRouter(prefix="/api/auth/roles", tags=["roles"])


# ── Read ──────────────────────────────────────────────────────────────────────


@router.get(
    "",
    summary="List all roles",
    description="Returns all active roles with their permissions.",
)
async def list_roles(
    current_user: User = Depends(require_permission("roles:read")),
    db: AsyncSession = Depends(get_db),
):
    svc = RoleService(db)
    roles = await svc.list_roles()
    return success_response(data=[RoleWithPermissionsResponse.model_validate(r).model_dump() for r in roles])


@router.get(
    "/{role_id}",
    summary="Get role detail",
    description="Returns a single role with its assigned permissions.",
)
async def get_role(
    role_id: uuid.UUID,
    current_user: User = Depends(require_permission("roles:read")),
    db: AsyncSession = Depends(get_db),
):
    svc = RoleService(db)
    role = await svc.get_role(role_id)
    return success_response(data=RoleWithPermissionsResponse.model_validate(role).model_dump())


# ── Create ────────────────────────────────────────────────────────────────────


@router.post(
    "",
    summary="Create role",
    description="Creates a new role.",
    status_code=status.HTTP_201_CREATED,
)
async def create_role(
    body: CreateRoleRequest,
    current_user: User = Depends(require_permission("roles:write")),
    db: AsyncSession = Depends(get_db),
):
    svc = RoleService(db)
    role = await svc.create_role(body.name, body.short_name, body.description)
    return success_response(
        data=RoleWithPermissionsResponse.model_validate(role).model_dump(),
        message="Role created",
    )


# ── Update ────────────────────────────────────────────────────────────────────


@router.patch(
    "/{role_id}",
    summary="Update role",
    description="Partially updates a role's name, short_name, or description.",
)
async def update_role(
    role_id: uuid.UUID,
    body: UpdateRoleRequest,
    current_user: User = Depends(require_permission("roles:write")),
    db: AsyncSession = Depends(get_db),
):
    svc = RoleService(db)
    role = await svc.update_role(role_id, body.name, body.short_name, body.description)
    return success_response(
        data=RoleWithPermissionsResponse.model_validate(role).model_dump(),
        message="Role updated",
    )


# ── Delete ────────────────────────────────────────────────────────────────────


@router.delete(
    "/{role_id}",
    summary="Delete role",
    description="Soft-deletes a role. Fails if any active users are still assigned to it.",
    status_code=status.HTTP_200_OK,
)
async def delete_role(
    role_id: uuid.UUID,
    current_user: User = Depends(require_permission("roles:delete")),
    db: AsyncSession = Depends(get_db),
):
    svc = RoleService(db)
    await svc.delete_role(role_id)
    return success_response(message="Role deleted")


# ── Assign / Unassign ─────────────────────────────────────────────────────────


@router.post(
    "/{role_id}/assign/{user_id}",
    summary="Assign role to user",
    description="Assigns the specified role to a user, replacing any existing role.",
)
async def assign_role(
    role_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: User = Depends(require_permission("roles:write")),
    db: AsyncSession = Depends(get_db),
):
    svc = RoleService(db)
    user = await svc.assign_role(user_id, role_id)
    return success_response(
        data=UserWithProfileResponse.model_validate(user).model_dump(),
        message="Role assigned",
    )


@router.delete(
    "/unassign/{user_id}",
    summary="Unassign role from user",
    description="Removes the role from a user, leaving them with no role.",
)
async def unassign_role(
    user_id: uuid.UUID,
    current_user: User = Depends(require_permission("roles:write")),
    db: AsyncSession = Depends(get_db),
):
    svc = RoleService(db)
    user = await svc.unassign_role(user_id)
    return success_response(
        data=UserWithProfileResponse.model_validate(user).model_dump(),
        message="Role unassigned",
    )
