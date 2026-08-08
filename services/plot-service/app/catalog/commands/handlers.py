"""Command handlers — direct DB writes against the furniture catalog.

Unlike plots, catalog items are low-frequency reference data (admin-managed),
not a per-user event stream — no Kafka publishing here.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.models.catalog_models import FurnitureCatalogItem
from app.catalog.schemas.request.catalog_commands import CreateCatalogItemCommand, UpdateCatalogItemCommand


async def handle_create_item(cmd: CreateCatalogItemCommand, db: AsyncSession) -> FurnitureCatalogItem:
    item = FurnitureCatalogItem(
        name=cmd.name,
        category=cmd.category,
        width=cmd.width,
        height=cmd.height,
        depth=cmd.depth,
        default_color=cmd.default_color,
        price=cmd.price,
        description=cmd.description,
    )
    db.add(item)
    await db.flush()
    return item


async def handle_update_item(cmd: UpdateCatalogItemCommand, db: AsyncSession) -> FurnitureCatalogItem | None:
    result = await db.execute(
        select(FurnitureCatalogItem).where(
            FurnitureCatalogItem.id == cmd.item_id,
            FurnitureCatalogItem.is_deleted.is_(False),
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        return None

    if cmd.name is not None:
        item.name = cmd.name
    if cmd.category is not None:
        item.category = cmd.category
    if cmd.width is not None:
        item.width = cmd.width
    if cmd.height is not None:
        item.height = cmd.height
    if cmd.depth is not None:
        item.depth = cmd.depth
    if cmd.default_color is not None:
        item.default_color = cmd.default_color
    if cmd.price is not None:
        item.price = cmd.price
    if cmd.description is not None:
        item.description = cmd.description
    await db.flush()
    return item


async def handle_delete_item(item_id: uuid.UUID, db: AsyncSession) -> None:
    result = await db.execute(
        select(FurnitureCatalogItem).where(
            FurnitureCatalogItem.id == item_id,
            FurnitureCatalogItem.is_deleted.is_(False),
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        return
    item.is_deleted = True
    await db.flush()
