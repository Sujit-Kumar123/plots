import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.queries.handlers import get_plot, list_plots, search_plots

router = APIRouter()


def _user_id(x_user_id: str = Header(...)) -> uuid.UUID:
    try:
        return uuid.UUID(x_user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid X-User-ID header")


@router.get("/plots")
async def get_plots(
    user_id: uuid.UUID = Depends(_user_id),
    session_id: uuid.UUID | None = Query(default=None),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await list_plots(user_id, db, session_id, limit, offset)


@router.get("/plots/search")
async def search(
    q: str = Query(..., min_length=1),
    user_id: uuid.UUID = Depends(_user_id),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await search_plots(user_id, q, db, limit, offset)


@router.get("/plots/{plot_id}")
async def get_single_plot(
    plot_id: uuid.UUID,
    user_id: uuid.UUID = Depends(_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await get_plot(plot_id, user_id, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plot not found")
    return result
