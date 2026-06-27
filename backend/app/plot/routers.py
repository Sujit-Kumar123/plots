import uuid
from math import ceil

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_permission
from app.auth.models import User
from app.common.pagination import PaginatedResponse, PaginationParams
from app.common.responses import success_response
from app.database import get_db
from app.plot.schemas import SheetCreate, SheetListItem, SheetResponse, SheetUpdate
from app.plot.services import SheetService

router = APIRouter(prefix="/api/plot/sheets", tags=["plot"])


@router.post("")
async def create_sheet(
    body: SheetCreate,
    current_user: User = Depends(require_permission("sheets:write")),
    db: AsyncSession = Depends(get_db),
):
    sheet = await SheetService(db).create(current_user.id, body)
    return success_response(data=SheetResponse.model_validate(sheet).model_dump())


@router.get("")
async def list_sheets(
    pagination: PaginationParams = Depends(),
    search: str | None = Query(None, description="Filter sheets by name"),
    current_user: User = Depends(require_permission("sheets:read")),
    db: AsyncSession = Depends(get_db),
):
    sheets, total = await SheetService(db).list(
        current_user.id,
        page=pagination.page,
        page_size=pagination.page_size,
        search=search or None,
    )
    return success_response(
        data=PaginatedResponse(
            items=[SheetListItem.model_validate(s).model_dump() for s in sheets],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=ceil(total / pagination.page_size) if total > 0 else 0,
        ).model_dump()
    )


@router.get("/{sheet_id}")
async def get_sheet(
    sheet_id: uuid.UUID,
    current_user: User = Depends(require_permission("sheets:read")),
    db: AsyncSession = Depends(get_db),
):
    sheet = await SheetService(db).get(sheet_id, current_user.id)
    return success_response(data=SheetResponse.model_validate(sheet).model_dump())


@router.put("/{sheet_id}")
async def update_sheet(
    sheet_id: uuid.UUID,
    body: SheetUpdate,
    current_user: User = Depends(require_permission("sheets:write")),
    db: AsyncSession = Depends(get_db),
):
    sheet = await SheetService(db).update(sheet_id, current_user.id, body)
    return success_response(data=SheetResponse.model_validate(sheet).model_dump())


@router.delete("/{sheet_id}")
async def delete_sheet(
    sheet_id: uuid.UUID,
    current_user: User = Depends(require_permission("sheets:delete")),
    db: AsyncSession = Depends(get_db),
):
    await SheetService(db).delete(sheet_id, current_user.id)
    return success_response(data=None, message="Sheet deleted")
