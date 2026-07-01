"""Kafka consumer — keeps the unified plot model in sync with domain events."""
import asyncio
import json
import logging
import uuid
from datetime import datetime

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from sqlalchemy import update

from app.config import settings
from app.database import async_session_factory
from app.models import Plot

logger = logging.getLogger(__name__)
_consumer_healthy: bool = False


def is_consumer_healthy() -> bool:
    return _consumer_healthy


async def _on_plot_created(payload: dict) -> None:
    async with async_session_factory() as session:
        elements = payload.get("elements", {})
        plot = Plot(
            id=uuid.UUID(payload["plot_id"]),
            user_id=uuid.UUID(payload["user_id"]),
            session_id=uuid.UUID(payload["session_id"]) if payload.get("session_id") else None,
            name=payload["name"],
            sheet_w=payload["sheet_w"],
            sheet_d=payload["sheet_d"],
            grid_step=payload["grid_step"],
            elements=elements,
            version=payload["version"],
            element_count=sum(len(v) if isinstance(v, list) else 1 for v in elements.values()),
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
            values["element_count"] = sum(
                len(v) if isinstance(v, list) else 1 for v in elements.values()
            )
        await session.execute(
            update(Plot).where(Plot.id == uuid.UUID(payload["plot_id"])).values(**values)
        )
        await session.commit()


async def _on_plot_deleted(payload: dict) -> None:
    async with async_session_factory() as session:
        await session.execute(
            update(Plot).where(Plot.id == uuid.UUID(payload["plot_id"])).values(is_deleted=True)
        )
        await session.commit()


async def _noop(payload: dict) -> None:
    pass


_HANDLERS = {
    "plot.created": _on_plot_created,
    "plot.updated": _on_plot_updated,
    "plot.deleted": _on_plot_deleted,
    "plot.bulk.created": _noop,
}


async def _publish_to_dlq(
    dlq_producer: AIOKafkaProducer, topic: str, msg_value: dict, error: str
) -> None:
    dlq_topic = f"{topic}.dlq"
    dlq_payload = {
        "original_payload": msg_value,
        "error": error,
        "failed_at": datetime.utcnow().isoformat(),
        "service": "plot-service",
    }
    try:
        await dlq_producer.send_and_wait(dlq_topic, value=json.dumps(dlq_payload, default=str).encode())
        logger.info("Published failed event to DLQ topic %s", dlq_topic)
    except Exception as dlq_exc:
        logger.error("Failed to publish to DLQ %s: %s — event will be lost", dlq_topic, dlq_exc)


async def _handle_with_retry(
    handler, msg_value: dict, dlq_producer: AIOKafkaProducer, topic: str, event_type: str
) -> None:
    last_exc: Exception | None = None
    for attempt in range(1, settings.kafka_consumer_max_retries + 1):
        try:
            await handler(msg_value)
            return
        except Exception as exc:
            last_exc = exc
            logger.warning(
                "Projection attempt %d/%d failed event=%s: %s",
                attempt, settings.kafka_consumer_max_retries, event_type, exc,
            )
            if attempt < settings.kafka_consumer_max_retries:
                await asyncio.sleep(settings.kafka_consumer_retry_backoff * attempt)

    logger.error(
        "Projection permanently failed event=%s after %d attempts, sending to DLQ",
        event_type, settings.kafka_consumer_max_retries,
    )
    await _publish_to_dlq(dlq_producer, topic, msg_value, str(last_exc))


async def run_consumer() -> None:
    global _consumer_healthy
    dlq_producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        value_serializer=lambda v: v if isinstance(v, bytes) else v.encode(),
    )
    try:
        await asyncio.wait_for(dlq_producer.start(), timeout=30.0)
    except Exception as exc:
        logger.error("DLQ producer failed to start: %s", exc)
        raise
    consumer = AIOKafkaConsumer(
        settings.topic_plot_events,
        settings.topic_plot_bulk,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.kafka_consumer_group,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        value_deserializer=lambda v: json.loads(v.decode()),
    )
    try:
        await asyncio.wait_for(consumer.start(), timeout=30.0)
    except Exception as exc:
        logger.error("Kafka consumer failed to start: %s", exc)
        await dlq_producer.stop()
        raise
    _consumer_healthy = True
    logger.info("Plot projector consumer started (manual commit mode)")
    try:
        async for msg in consumer:
            event_type = msg.value.get("event_type")
            handler = _HANDLERS.get(event_type)
            if handler:
                await _handle_with_retry(handler, msg.value, dlq_producer, msg.topic, event_type)
            else:
                logger.warning("Unknown event type: %s — skipping", event_type)
            await consumer.commit()
    except asyncio.CancelledError:
        logger.info("Consumer task cancelled — shutting down")
        raise
    except Exception as exc:
        logger.critical("Consumer loop crashed: %s", exc, exc_info=True)
        _consumer_healthy = False
        raise
    finally:
        _consumer_healthy = False
        await consumer.stop()
        await dlq_producer.stop()
        logger.info("Plot projector consumer stopped")
