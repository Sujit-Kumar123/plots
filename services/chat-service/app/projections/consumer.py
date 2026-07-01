"""Kafka consumer — updates the read model when domain events arrive."""
import asyncio
import json
import logging
import uuid
from datetime import datetime

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaError
from sqlalchemy import select, update

from app.config import settings
from app.database import async_session_factory
from app.read_models import ChatMessageReadModel, ChatSessionReadModel

logger = logging.getLogger(__name__)
_consumer_healthy: bool = False


def is_consumer_healthy() -> bool:
    return _consumer_healthy


async def _upsert_message(payload: dict) -> None:
    async with async_session_factory() as session:
        message = ChatMessageReadModel(
            id=uuid.UUID(payload["message_id"]),
            session_id=uuid.UUID(payload["session_id"]),
            user_id=uuid.UUID(payload["user_id"]),
            role=payload["role"],
            content=payload["content"],
            model=payload.get("model"),
            token_count=payload.get("token_count"),
        )
        await session.merge(message)

        # Upsert session read model — create if first message, otherwise increment
        result = await session.execute(
            select(ChatSessionReadModel).where(
                ChatSessionReadModel.id == uuid.UUID(payload["session_id"])
            )
        )
        session_rm = result.scalar_one_or_none()
        if session_rm is None:
            session_rm = ChatSessionReadModel(
                id=uuid.UUID(payload["session_id"]),
                user_id=uuid.UUID(payload["user_id"]),
                title="New Chat",
                message_count=1,
                last_message_preview=payload["content"][:200],
            )
            session.add(session_rm)
        else:
            session_rm.message_count += 1
            session_rm.last_message_preview = payload["content"][:200]

        await session.commit()


async def _soft_delete_message(payload: dict) -> None:
    async with async_session_factory() as session:
        await session.execute(
            update(ChatMessageReadModel)
            .where(ChatMessageReadModel.id == uuid.UUID(payload["message_id"]))
            .values(is_deleted=True)
        )
        await session.commit()


async def _upsert_bulk_messages(payload: dict) -> None:
    async with async_session_factory() as session:
        result = await session.execute(
            select(ChatSessionReadModel).where(
                ChatSessionReadModel.id == uuid.UUID(payload["session_id"])
            )
        )
        session_rm = result.scalar_one_or_none()
        if session_rm is None:
            session_rm = ChatSessionReadModel(
                id=uuid.UUID(payload["session_id"]),
                user_id=uuid.UUID(payload["user_id"]),
                title="New Chat",
                message_count=payload["count"],
                last_message_preview=None,
            )
            session.add(session_rm)
        else:
            session_rm.message_count += payload["count"]

        await session.commit()


_HANDLERS = {
    "chat.message.created": _upsert_message,
    "chat.message.deleted": _soft_delete_message,
    "chat.bulk.messages.created": _upsert_bulk_messages,
}


async def _publish_to_dlq(
    dlq_producer: AIOKafkaProducer, topic: str, msg_value: dict, error: str
) -> None:
    dlq_topic = f"{topic}.dlq"
    dlq_payload = {
        "original_payload": msg_value,
        "error": error,
        "failed_at": datetime.utcnow().isoformat(),
        "service": "chat-service",
    }
    try:
        await dlq_producer.send_and_wait(
            dlq_topic,
            value=json.dumps(dlq_payload, default=str).encode(),
        )
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
        settings.topic_chat_events,
        settings.topic_chat_bulk,
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
    logger.info("Chat projector consumer started (manual commit mode)")
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
        logger.info("Chat projector consumer stopped")
