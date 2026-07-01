import uuid
from math import ceil

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_permission
from app.auth.models import User
from app.auth.schemas import (
    CreatePermissionRequest,
    PermissionResponse,
    RoleWithPermissionsResponse,
    UpdatePermissionRequest,
)
from app.auth.service import PermissionService
from app.common.pagination import PaginatedResponse, PaginationParams
from app.common.responses import success_response
from app.database import get_db

router = APIRouter(prefix="/api/auth/permissions", tags=["permissions"])


# ── Read ──────────────────────────────────────────────────────────────────────


@router.get(
    "",
    summary="List all permissions",
    description="Returns active permissions ordered by name, paginated.",
)
async def list_permissions(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(require_permission("permissions:read")),
    db: AsyncSession = Depends(get_db),
):
    svc = PermissionService(db)
    perms, total = await svc.list_permissions(pagination)
    return success_response(
        data=PaginatedResponse(
            items=[PermissionResponse.model_validate(p).model_dump() for p in perms],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=ceil(total / pagination.page_size) if total > 0 else 0,
        ).model_dump()
    )


@router.get(
    "/missing",
    summary="List missing permission codes",
    description="Returns codes from the built-in PERMISSIONS list that are not yet in the database.",
)
async def list_missing_permissions(
    current_user: User = Depends(require_permission("permissions:read")),
    db: AsyncSession = Depends(get_db),
):
    svc = PermissionService(db)
    codes = await svc.list_missing_permission_codes()
    return success_response(data=codes)


@router.get(
    "/{permission_id}",
    summary="Get permission detail",
    description="Returns a single permission by ID.",
)
async def get_permission(
    permission_id: uuid.UUID,
    current_user: User = Depends(require_permission("permissions:read")),
    db: AsyncSession = Depends(get_db),
):
    svc = PermissionService(db)
    perm = await svc.get_permission(permission_id)
    return success_response(data=PermissionResponse.model_validate(perm).model_dump())


# ── Create ────────────────────────────────────────────────────────────────────


@router.post(
    "",
    summary="Create permission",
    description="Creates a new permission. `code` must be unique.",
    status_code=status.HTTP_201_CREATED,
)
async def create_permission(
    body: CreatePermissionRequest,
    current_user: User = Depends(require_permission("permissions:write")),
    db: AsyncSession = Depends(get_db),
):
    svc = PermissionService(db)
    perm = await svc.create_permission(body.name, body.code, body.description)
    return success_response(
        data=PermissionResponse.model_validate(perm).model_dump(),
        message="Permission created",
    )


# ── Update ────────────────────────────────────────────────────────────────────


@router.patch(
    "/{permission_id}",
    summary="Update permission",
    description="Partially updates a permission's name, code, or description.",
)
async def update_permission(
    permission_id: uuid.UUID,
    body: UpdatePermissionRequest,
    current_user: User = Depends(require_permission("permissions:write")),
    db: AsyncSession = Depends(get_db),
):
    svc = PermissionService(db)
    perm = await svc.update_permission(permission_id, body.name, body.code, body.description)
    return success_response(
        data=PermissionResponse.model_validate(perm).model_dump(),
        message="Permission updated",
    )


# ── Delete ────────────────────────────────────────────────────────────────────


@router.delete(
    "/{permission_id}",
    summary="Delete permission",
    description=("Soft-deletes a permission. Fails if the permission is currently assigned to any role."),
    status_code=status.HTTP_200_OK,
)
async def delete_permission(
    permission_id: uuid.UUID,
    current_user: User = Depends(require_permission("permissions:delete")),
    db: AsyncSession = Depends(get_db),
):
    svc = PermissionService(db)
    await svc.delete_permission(permission_id)
    return success_response(message="Permission deleted")


# ── Assign / Unassign to Role ─────────────────────────────────────────────────


@router.post(
    "/{permission_id}/assign/{role_id}",
    summary="Assign permission to role",
    description="Adds a permission to a role. Raises 409 if already assigned.",
)
async def assign_to_role(
    permission_id: uuid.UUID,
    role_id: uuid.UUID,
    current_user: User = Depends(require_permission("permissions:write")),
    db: AsyncSession = Depends(get_db),
):
    svc = PermissionService(db)
    role = await svc.assign_to_role(role_id, permission_id)
    return success_response(
        data=RoleWithPermissionsResponse.model_validate(role).model_dump(),
        message="Permission assigned to role",
    )


@router.delete(
    "/{permission_id}/unassign/{role_id}",
    summary="Unassign permission from role",
    description="Removes a permission from a role. Raises 404 if not assigned.",
)
async def unassign_from_role(
    permission_id: uuid.UUID,
    role_id: uuid.UUID,
    current_user: User = Depends(require_permission("permissions:write")),
    db: AsyncSession = Depends(get_db),
):
    svc = PermissionService(db)
    role = await svc.unassign_from_role(role_id, permission_id)
    return success_response(
        data=RoleWithPermissionsResponse.model_validate(role).model_dump(),
        message="Permission unassigned from role",
    )
