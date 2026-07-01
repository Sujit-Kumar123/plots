from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_permission
from app.auth.models import User
from app.auth.schemas import (
    ChangePasswordRequest,
    PermissionResponse,
    RoleResponse,
    UpdateProfileRequest,
    UserWithProfileResponse,
)
from app.auth.service import ProfileService
from app.common.responses import success_response
from app.database import get_db

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get(
    "/me",
    summary="Get my profile",
    description="Returns the authenticated user's full profile including role.",
)
async def get_my_profile(
    current_user: User = Depends(require_permission("profile:read")),
    db: AsyncSession = Depends(get_db),
):
    svc = ProfileService(db)
    user = await svc.get_user_with_profile(current_user.id)
    return success_response(data=UserWithProfileResponse.model_validate(user).model_dump())


@router.get(
    "/me/role",
    summary="Get my role",
    description="Returns the authenticated user's assigned role, or null if no role is assigned.",
)
async def get_my_role(
    current_user: User = Depends(require_permission("profile:read")),
    db: AsyncSession = Depends(get_db),
):
    svc = ProfileService(db)
    user = await svc.get_user_with_profile(current_user.id)
    data = RoleResponse.model_validate(user.role).model_dump() if user.role else None
    return success_response(data=data)


@router.get(
    "/me/permissions",
    summary="Get my permissions",
    description="Returns all permissions granted to the authenticated user via their role.",
)
async def get_my_permissions(
    current_user: User = Depends(require_permission("profile:read")),
    db: AsyncSession = Depends(get_db),
):
    svc = ProfileService(db)
    user = await svc.get_user_with_profile(current_user.id)
    permissions = [rp.permission for rp in user.role.role_permissions] if user.role else []
    return success_response(data=[PermissionResponse.model_validate(p).model_dump() for p in permissions])


@router.patch(
    "/me",
    summary="Update my profile",
    description=(
        "Partially update the authenticated user's profile. "
        "Only provided fields are updated — omitted fields are left unchanged."
    ),
    status_code=status.HTTP_200_OK,
)
async def update_my_profile(
    body: UpdateProfileRequest,
    current_user: User = Depends(require_permission("profile:write")),
    db: AsyncSession = Depends(get_db),
):
    svc = ProfileService(db)
    await svc.update_profile(
        current_user.id,
        fname=body.fname,
        lname=body.lname,
        phone=body.phone,
        company=body.company,
        department=body.department,
        designation=body.designation,
        company_role=body.company_role,
        location=body.location,
        photo=body.photo,
    )
    user = await svc.get_user_with_profile(current_user.id)
    return success_response(
        data=UserWithProfileResponse.model_validate(user).model_dump(),
        message="Profile updated",
    )


@router.put(
    "/me/password",
    summary="Change my password",
    description=("Change the authenticated user's password. Requires the current password for verification."),
    status_code=status.HTTP_200_OK,
)
async def change_my_password(
    body: ChangePasswordRequest,
    current_user: User = Depends(require_permission("profile:write")),
    db: AsyncSession = Depends(get_db),
):
    svc = ProfileService(db)
    await svc.change_password(current_user.id, body.current_password, body.new_password)
    return success_response(message="Password changed successfully")
