"""Query handlers — read-only operations against the furniture catalog."""
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.catalog.models.catalog_models import FurnitureCatalogItem


def _serialize(item: FurnitureCatalogItem) -> dict:
    return {
        "id": str(item.id),
        "name": item.name,
        "category": item.category,
        "width": item.width,
        "height": item.height,
        "depth": item.depth,
        "default_color": item.default_color,
        "price": item.price,
        "description": item.description,
        "created_at": item.created_at.isoformat(),
        "updated_at": item.updated_at.isoformat(),
    }


async def get_catalog_item(item_id: uuid.UUID, db: AsyncSession) -> dict | None:
    result = await db.execute(
        select(FurnitureCatalogItem).where(
            FurnitureCatalogItem.id == item_id,
            FurnitureCatalogItem.is_deleted.is_(False),
        )
    )
    item = result.scalar_one_or_none()
    return _serialize(item) if item else None


async def list_catalog_items(
    db: AsyncSession,
    category: str | None = None,
    q: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict:
    filters = [FurnitureCatalogItem.is_deleted.is_(False)]
    if category:
        filters.append(FurnitureCatalogItem.category == category)
    if q:
        filters.append(FurnitureCatalogItem.name.ilike(f"%{q}%"))

    count_q = await db.execute(select(func.count()).where(*filters))
    total = count_q.scalar_one()

    result = await db.execute(
        select(FurnitureCatalogItem)
        .where(*filters)
        .order_by(FurnitureCatalogItem.category, FurnitureCatalogItem.name)
        .limit(limit)
        .offset(offset)
    )
    items = result.scalars().all()
    return {"total": total, "limit": limit, "offset": offset, "items": [_serialize(i) for i in items]}
