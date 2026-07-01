import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.commands.handlers import (
    handle_bulk_create_plots,
    handle_create_plot,
    handle_delete_plot,
    handle_update_plot,
)
from app.commands.schemas import BulkCreatePlotsCommand, CreatePlotCommand, DeletePlotCommand, UpdatePlotCommand
from app.database import get_db
from app.queries.handlers import get_plot, list_plots, search_plots
from app.schemas import BulkPlotsAcceptedResponse, PlotCommandResponse, PlotItem, PlotListResponse

router = APIRouter()

_ERR = {
    400: {"description": "Bad request — invalid UUID or body"},
    401: {"description": "Missing or invalid auth token"},
    403: {"description": "Forbidden — invalid internal secret"},
    404: {"description": "Plot not found"},
    422: {"description": "Validation error"},
}


def _user_id(x_user_id: str = Header(..., description="UUID of the authenticated user (injected by gateway)")) -> uuid.UUID:
    try:
        return uuid.UUID(x_user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid X-User-ID header")


# ── Command endpoints ─────────────────────────────────────────────────────────

@router.post(
    "/plots",
    status_code=201,
    response_model=PlotCommandResponse,
    summary="Create a plot (sheet)",
    description=(
        "Creates a new plot with its initial elements. "
        "Publishes a `plot.created` event to Kafka for read-model projection."
    ),
    responses={**_ERR},
    tags=["plots"],
)
async def create_plot(
    cmd: CreatePlotCommand,
    user_id: uuid.UUID = Depends(_user_id),
    db: AsyncSession = Depends(get_db),
):
    plot = await handle_create_plot(cmd, user_id, db)
    return {"id": str(plot.id), "name": plot.name, "version": plot.version}


@router.post(
    "/plots/bulk",
    status_code=202,
    response_model=BulkPlotsAcceptedResponse,
    summary="Bulk-create plots",
    description="Accepts up to 500 plots in a single request. Returns 202 immediately.",
    responses={**_ERR},
    tags=["plots"],
)
async def create_plots_bulk(
    cmd: BulkCreatePlotsCommand,
    user_id: uuid.UUID = Depends(_user_id),
    db: AsyncSession = Depends(get_db),
):
    ids = await handle_bulk_create_plots(cmd, user_id, db)
    return {"accepted": len(ids), "ids": [str(i) for i in ids]}


@router.put(
    "/plots/{plot_id}",
    response_model=PlotCommandResponse,
    summary="Update a plot",
    description=(
        "Partially updates a plot's properties. Only provided fields are changed. "
        "Increments the version counter on each update."
    ),
    responses={**_ERR},
    tags=["plots"],
)
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
    return {"id": str(plot.id), "name": plot.name, "version": plot.version}


@router.delete(
    "/plots/{plot_id}",
    status_code=204,
    summary="Delete a plot",
    description="Soft-deletes a plot. The record is retained for audit purposes.",
    responses={**_ERR},
    tags=["plots"],
)
async def delete_plot(
    plot_id: uuid.UUID,
    user_id: uuid.UUID = Depends(_user_id),
    db: AsyncSession = Depends(get_db),
):
    await handle_delete_plot(DeletePlotCommand(plot_id=plot_id), user_id, db)


# ── Query endpoints ───────────────────────────────────────────────────────────

@router.get(
    "/plots/search",
    response_model=PlotListResponse,
    summary="Search plots by name",
    description="Case-insensitive substring search on the plot name. Returns paginated results.",
    responses={**_ERR},
    tags=["plots"],
)
async def search(
    q: str = Query(..., min_length=1, description="Search query (matched against plot name)"),
    user_id: uuid.UUID = Depends(_user_id),
    limit: int = Query(default=20, le=100, description="Maximum items to return"),
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
    db: AsyncSession = Depends(get_db),
):
    return await search_plots(user_id, q, db, limit, offset)


@router.get(
    "/plots",
    response_model=PlotListResponse,
    summary="List plots",
    description=(
        "Returns a paginated list of plots for the authenticated user, "
        "ordered by most recently updated. Filter by `session_id` to scope results."
    ),
    responses={**_ERR},
    tags=["plots"],
)
async def get_plots(
    user_id: uuid.UUID = Depends(_user_id),
    session_id: uuid.UUID | None = Query(default=None, description="Filter by chat session UUID"),
    limit: int = Query(default=20, le=100, description="Maximum items to return"),
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
    db: AsyncSession = Depends(get_db),
):
    return await list_plots(user_id, db, session_id, limit, offset)


@router.get(
    "/plots/{plot_id}",
    response_model=PlotItem,
    summary="Get a single plot",
    description="Returns the full plot data including all elements.",
    responses={**_ERR},
    tags=["plots"],
)
async def get_single_plot(
    plot_id: uuid.UUID,
    user_id: uuid.UUID = Depends(_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await get_plot(plot_id, user_id, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plot not found")
    return result
