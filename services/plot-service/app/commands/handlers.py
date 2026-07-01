"""Command handlers — orchestrate DB write + Kafka publish."""
import uuid
from datetime import datetime, timezone


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.commands.schemas import (
    BulkCreatePlotsCommand,
    CreatePlotCommand,
    DeletePlotCommand,
    UpdatePlotCommand,
)
from app.config import settings
from app.events import publisher
from app.events.schemas import PlotBulkCreatedEvent, PlotCreatedEvent, PlotDeletedEvent, PlotUpdatedEvent
from app.models import Plot


async def handle_create_plot(cmd: CreatePlotCommand, user_id: uuid.UUID, db: AsyncSession) -> Plot:
    plot = Plot(
        user_id=user_id,
        session_id=cmd.session_id,
        name=cmd.name,
        sheet_w=cmd.sheet_w,
        sheet_d=cmd.sheet_d,
        grid_step=cmd.grid_step,
        elements=cmd.elements,
        element_count=sum(len(v) if isinstance(v, list) else 1 for v in cmd.elements.values()),
    )
    db.add(plot)
    await db.flush()

    event = PlotCreatedEvent(
        plot_id=plot.id,
        user_id=user_id,
        session_id=plot.session_id,
        name=plot.name,
        sheet_w=plot.sheet_w,
        sheet_d=plot.sheet_d,
        grid_step=plot.grid_step,
        elements=plot.elements,
        version=plot.version,
        created_at=plot.created_at,
    )
    await publisher.publish(settings.topic_plot_events, event, key=str(user_id))
    return plot


async def handle_bulk_create_plots(
    cmd: BulkCreatePlotsCommand, user_id: uuid.UUID, db: AsyncSession
) -> list[uuid.UUID]:
    plots = [
        Plot(
            user_id=user_id,
            session_id=p.session_id,
            name=p.name,
            sheet_w=p.sheet_w,
            sheet_d=p.sheet_d,
            grid_step=p.grid_step,
            elements=p.elements,
            element_count=sum(len(v) if isinstance(v, list) else 1 for v in p.elements.values()),
        )
        for p in cmd.plots
    ]
    db.add_all(plots)
    await db.flush()

    ids = [p.id for p in plots]
    event = PlotBulkCreatedEvent(
        user_id=user_id,
        plot_ids=ids,
        count=len(ids),
        created_at=datetime.now(timezone.utc),
    )
    await publisher.publish(settings.topic_plot_bulk, event, key=str(user_id))
    return ids


async def handle_update_plot(cmd: UpdatePlotCommand, user_id: uuid.UUID, db: AsyncSession) -> Plot | None:
    result = await db.execute(
        select(Plot).where(
            Plot.id == cmd.plot_id,
            Plot.user_id == user_id,
            Plot.is_deleted.is_(False),
        )
    )
    plot = result.scalar_one_or_none()
    if not plot:
        return None

    if cmd.name is not None:
        plot.name = cmd.name
    if cmd.sheet_w is not None:
        plot.sheet_w = cmd.sheet_w
    if cmd.sheet_d is not None:
        plot.sheet_d = cmd.sheet_d
    if cmd.grid_step is not None:
        plot.grid_step = cmd.grid_step
    if cmd.elements is not None:
        plot.elements = cmd.elements
        plot.element_count = sum(len(v) if isinstance(v, list) else 1 for v in cmd.elements.values())
    plot.version += 1
    await db.flush()

    event = PlotUpdatedEvent(
        plot_id=plot.id,
        user_id=user_id,
        name=cmd.name,
        elements=cmd.elements,
        version=plot.version,
        updated_at=datetime.now(timezone.utc),
    )
    await publisher.publish(settings.topic_plot_events, event, key=str(user_id))
    return plot


async def handle_delete_plot(cmd: DeletePlotCommand, user_id: uuid.UUID, db: AsyncSession) -> None:
    result = await db.execute(
        select(Plot).where(
            Plot.id == cmd.plot_id,
            Plot.user_id == user_id,
            Plot.is_deleted.is_(False),
        )
    )
    plot = result.scalar_one_or_none()
    if not plot:
        return

    plot.is_deleted = True
    await db.flush()

    event = PlotDeletedEvent(
        plot_id=plot.id,
        user_id=user_id,
        deleted_at=datetime.now(timezone.utc),
    )
    await publisher.publish(settings.topic_plot_events, event, key=str(user_id))
