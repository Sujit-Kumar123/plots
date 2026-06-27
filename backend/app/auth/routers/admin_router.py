import uuid
from math import ceil

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.service.admin_service import (
    activate_user,
    deactivate_user,
    get_user_detail,
    list_users,
    soft_delete_user,
    update_user,
)
from app.auth.dependencies import require_permission
from app.auth.models import User
from app.auth.schemas import UserResponse, UserWithProfileResponse
from app.common.pagination import PaginatedResponse, PaginationParams
from app.common.responses import success_response
from app.database import get_db

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users")
async def get_users(
    pagination: PaginationParams = Depends(),
    role: str | None = Query(None),
    is_active: bool | None = Query(None),
    current_user: User = Depends(require_permission("users:read")),
    db: AsyncSession = Depends(get_db),
):
    users, total = await list_users(db, pagination, role, is_active)
    return success_response(
        data=PaginatedResponse(
            items=[UserWithProfileResponse.model_validate(u).model_dump() for u in users],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=ceil(total / pagination.page_size) if total > 0 else 0,
        ).model_dump()
    )


@router.get("/users/{user_id}")
async def get_user(
    user_id: uuid.UUID,
    current_user: User = Depends(require_permission("users:read")),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_detail(db, user_id)
    return success_response(data=UserWithProfileResponse.model_validate(user).model_dump())


@router.put("/users/{user_id}")
async def edit_user(
    user_id: uuid.UUID,
    role_id: uuid.UUID | None = Query(None),
    is_active: bool | None = Query(None),
    current_user: User = Depends(require_permission("users:write")),
    db: AsyncSession = Depends(get_db),
):
    user = await update_user(db, user_id, current_user, role_id, is_active)
    return success_response(data=UserResponse.model_validate(user).model_dump())


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: uuid.UUID,
    current_user: User = Depends(require_permission("users:delete")),
    db: AsyncSession = Depends(get_db),
):
    await soft_delete_user(db, user_id, current_user)
    return success_response(message="User deleted")


@router.post("/users/{user_id}/deactivate")
async def deactivate(
    user_id: uuid.UUID,
    current_user: User = Depends(require_permission("users:write")),
    db: AsyncSession = Depends(get_db),
):
    user = await deactivate_user(db, user_id, current_user)
    return success_response(data=UserResponse.model_validate(user).model_dump())


@router.post("/users/{user_id}/activate")
async def activate(
    user_id: uuid.UUID,
    current_user: User = Depends(require_permission("users:write")),
    db: AsyncSession = Depends(get_db),
):
    user = await activate_user(db, user_id)
    return success_response(data=UserResponse.model_validate(user).model_dump())
