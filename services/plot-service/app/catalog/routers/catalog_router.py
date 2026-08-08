import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.commands.handlers import handle_create_item, handle_delete_item, handle_update_item
from app.catalog.queries.handlers import get_catalog_item, list_catalog_items
from app.catalog.schemas.request.catalog_commands import CreateCatalogItemCommand, UpdateCatalogItemCommand
from app.catalog.schemas.response.catalog_schemas import CatalogItem, CatalogListResponse
from app.database import get_db

router = APIRouter()

_ERR = {
    400: {"description": "Bad request — invalid UUID or body"},
    401: {"description": "Missing or invalid auth token"},
    403: {"description": "Forbidden — invalid internal secret"},
    404: {"description": "Catalog item not found"},
    422: {"description": "Validation error"},
}


def _user_id(x_user_id: str = Header(..., description="UUID of the authenticated user (injected by gateway)")) -> uuid.UUID:
    try:
        return uuid.UUID(x_user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid X-User-ID header")


@router.get(
    "/catalog",
    response_model=CatalogListResponse,
    summary="List furniture catalog items",
    description="Returns a paginated list of furniture catalog items. Filter by `category` or search by `q`.",
    responses={**_ERR},
    tags=["catalog"],
)
async def list_items(
    _: uuid.UUID = Depends(_user_id),
    category: str | None = Query(default=None, description="Filter by category"),
    q: str | None = Query(default=None, min_length=1, description="Search query (matched against item name)"),
    limit: int = Query(default=20, le=100, description="Maximum items to return"),
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
    db: AsyncSession = Depends(get_db),
):
    return await list_catalog_items(db, category, q, limit, offset)


@router.get(
    "/catalog/{item_id}",
    response_model=CatalogItem,
    summary="Get a single catalog item",
    responses={**_ERR},
    tags=["catalog"],
)
async def get_item(
    item_id: uuid.UUID,
    _: uuid.UUID = Depends(_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await get_catalog_item(item_id, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalog item not found")
    return result


@router.post(
    "/catalog",
    status_code=201,
    response_model=CatalogItem,
    summary="Create a catalog item",
    responses={**_ERR},
    tags=["catalog"],
)
async def create_item(
    cmd: CreateCatalogItemCommand,
    _: uuid.UUID = Depends(_user_id),
    db: AsyncSession = Depends(get_db),
):
    item = await handle_create_item(cmd, db)
    return await get_catalog_item(item.id, db)


@router.put(
    "/catalog/{item_id}",
    response_model=CatalogItem,
    summary="Update a catalog item",
    responses={**_ERR},
    tags=["catalog"],
)
async def update_item(
    item_id: uuid.UUID,
    cmd: UpdateCatalogItemCommand,
    _: uuid.UUID = Depends(_user_id),
    db: AsyncSession = Depends(get_db),
):
    cmd.item_id = item_id
    item = await handle_update_item(cmd, db)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalog item not found")
    return await get_catalog_item(item.id, db)


@router.delete(
    "/catalog/{item_id}",
    status_code=204,
    summary="Delete a catalog item",
    responses={**_ERR},
    tags=["catalog"],
)
async def delete_item(
    item_id: uuid.UUID,
    _: uuid.UUID = Depends(_user_id),
    db: AsyncSession = Depends(get_db),
):
    await handle_delete_item(item_id, db)
