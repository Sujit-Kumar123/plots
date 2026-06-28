"""Kafka consumer — keeps the plot read model in sync with domain events."""
import asyncio
import json
import logging
import uuid

from aiokafka import AIOKafkaConsumer
from sqlalchemy import update

from app.config import settings
from app.database import async_session_factory
from app.models import PlotReadModel

logger = logging.getLogger(__name__)


async def _on_plot_created(payload: dict) -> None:
    async with async_session_factory() as session:
        elements = payload.get("elements", {})
        element_count = sum(len(v) if isinstance(v, list) else 1 for v in elements.values())
        plot = PlotReadModel(
            id=uuid.UUID(payload["plot_id"]),
            user_id=uuid.UUID(payload["user_id"]),
            session_id=uuid.UUID(payload["session_id"]) if payload.get("session_id") else None,
            name=payload["name"],
            sheet_w=payload["sheet_w"],
            sheet_d=payload["sheet_d"],
            grid_step=payload["grid_step"],
            elements=elements,
            version=payload["version"],
            element_count=element_count,
        )
        await session.merge(plot)
        await session.commit()


async def _on_plot_updated(payload: dict) -> None:
    async with async_session_factory() as session:
        values: dict = {"version": payload["version"]}
        if payload.get("name") is not None:
            values["name"] = payload["name"]
        if payload.get("elements") is not None:
            elements = payload["elements"]
            values["elements"] = elements
            values["element_count"] = sum(len(v) if isinstance(v, list) else 1 for v in elements.values())

        await session.execute(
            update(PlotReadModel)
            .where(PlotReadModel.id == uuid.UUID(payload["plot_id"]))
            .values(**values)
        )
        await session.commit()


async def _on_plot_deleted(payload: dict) -> None:
    async with async_session_factory() as session:
        await session.execute(
            update(PlotReadModel)
            .where(PlotReadModel.id == uuid.UUID(payload["plot_id"]))
            .values(is_deleted=True)
        )
        await session.commit()


_HANDLERS = {
    "plot.created": _on_plot_created,
    "plot.updated": _on_plot_updated,
    "plot.deleted": _on_plot_deleted,
    "plot.bulk.created": lambda _: asyncio.sleep(0),  # individual events handle the data
}


async def run_consumer() -> None:
    consumer = AIOKafkaConsumer(
        settings.topic_plot_events,
        settings.topic_plot_bulk,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.kafka_consumer_group,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda v: json.loads(v.decode()),
    )
    await consumer.start()
    logger.info("Plot query projector consumer started")
    try:
        async for msg in consumer:
            event_type = msg.value.get("event_type")
            handler = _HANDLERS.get(event_type)
            if handler:
                try:
                    await handler(msg.value)
                except Exception as exc:
                    logger.error("Failed to project plot event %s: %s", event_type, exc)
    finally:
        await consumer.stop()
