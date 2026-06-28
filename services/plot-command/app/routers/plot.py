import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.commands.handlers import (
    handle_bulk_create_plots,
    handle_create_plot,
    handle_delete_plot,
    handle_update_plot,
)
from app.commands.schemas import BulkCreatePlotsCommand, CreatePlotCommand, DeletePlotCommand, UpdatePlotCommand
from app.database import get_db

router = APIRouter()


def _user_id(x_user_id: str = Header(...)) -> uuid.UUID:
    try:
        return uuid.UUID(x_user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid X-User-ID header")


@router.post("/plots", status_code=201)
async def create_plot(
    cmd: CreatePlotCommand,
    user_id: uuid.UUID = Depends(_user_id),
    db: AsyncSession = Depends(get_db),
):
    plot = await handle_create_plot(cmd, user_id, db)
    return {"id": str(plot.id), "name": plot.name, "version": plot.version}


@router.post("/plots/bulk", status_code=202)
async def create_plots_bulk(
    cmd: BulkCreatePlotsCommand,
    user_id: uuid.UUID = Depends(_user_id),
    db: AsyncSession = Depends(get_db),
):
    ids = await handle_bulk_create_plots(cmd, user_id, db)
    return {"accepted": len(ids), "ids": [str(i) for i in ids]}


@router.put("/plots/{plot_id}")
async def update_plot(
    plot_id: uuid.UUID,
    cmd: UpdatePlotCommand,
    user_id: uuid.UUID = Depends(_user_id),
    db: AsyncSession = Depends(get_db),
):
    cmd.plot_id = plot_id
    plot = await handle_update_plot(cmd, user_id, db)
    if not plot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plot not found")
    return {"id": str(plot.id), "version": plot.version}


@router.delete("/plots/{plot_id}", status_code=204)
async def delete_plot(
    plot_id: uuid.UUID,
    user_id: uuid.UUID = Depends(_user_id),
    db: AsyncSession = Depends(get_db),
):
    await handle_delete_plot(DeletePlotCommand(plot_id=plot_id), user_id, db)
