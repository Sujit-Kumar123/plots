import uuid

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import PlotReadModel


def _serialize(p: PlotReadModel) -> dict:
    return {
        "id": str(p.id),
        "user_id": str(p.user_id),
        "session_id": str(p.session_id) if p.session_id else None,
        "name": p.name,
        "sheet_w": p.sheet_w,
        "sheet_d": p.sheet_d,
        "grid_step": p.grid_step,
        "elements": p.elements,
        "version": p.version,
        "element_count": p.element_count,
        "created_at": p.created_at.isoformat(),
        "updated_at": p.updated_at.isoformat(),
    }


async def get_plot(plot_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession) -> dict | None:
    result = await db.execute(
        select(PlotReadModel).where(
            PlotReadModel.id == plot_id,
            PlotReadModel.user_id == user_id,
            PlotReadModel.is_deleted.is_(False),
        )
    )
    p = result.scalar_one_or_none()
    return _serialize(p) if p else None


async def list_plots(
    user_id: uuid.UUID,
    db: AsyncSession,
    session_id: uuid.UUID | None = None,
    limit: int = 20,
    offset: int = 0,
) -> dict:
    filters = [PlotReadModel.user_id == user_id, PlotReadModel.is_deleted.is_(False)]
    if session_id:
        filters.append(PlotReadModel.session_id == session_id)

    count_q = await db.execute(select(func.count()).where(*filters))
    total = count_q.scalar_one()

    result = await db.execute(
        select(PlotReadModel)
        .where(*filters)
        .order_by(PlotReadModel.updated_at.desc())
        .limit(limit)
        .offset(offset)
    )
    plots = result.scalars().all()

    return {"total": total, "limit": limit, "offset": offset, "items": [_serialize(p) for p in plots]}


async def search_plots(
    user_id: uuid.UUID,
    query: str,
    db: AsyncSession,
    limit: int = 20,
    offset: int = 0,
) -> dict:
    like = f"%{query}%"
    filters = [
        PlotReadModel.user_id == user_id,
        PlotReadModel.is_deleted.is_(False),
        PlotReadModel.name.ilike(like),
    ]

    count_q = await db.execute(select(func.count()).where(*filters))
    total = count_q.scalar_one()

    result = await db.execute(
        select(PlotReadModel)
        .where(*filters)
        .order_by(PlotReadModel.updated_at.desc())
        .limit(limit)
        .offset(offset)
    )
    plots = result.scalars().all()

    return {"total": total, "limit": limit, "offset": offset, "items": [_serialize(p) for p in plots]}
