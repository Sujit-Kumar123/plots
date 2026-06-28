"""Kafka consumer — updates the read model when domain events arrive."""
import asyncio
import json
import logging
import uuid
from datetime import datetime

from aiokafka import AIOKafkaConsumer
from sqlalchemy import select, update

from app.config import settings
from app.database import async_session_factory
from app.models import ChatMessageReadModel, ChatSessionReadModel

logger = logging.getLogger(__name__)


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
        # Update session read model
        await session.execute(
            update(ChatSessionReadModel)
            .where(ChatSessionReadModel.id == uuid.UUID(payload["session_id"]))
            .values(
                message_count=ChatSessionReadModel.message_count + 1,
                last_message_preview=payload["content"][:200],
            )
        )
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
    # Bulk events carry only IDs; the actual data was already written by command service.
    # Query service fetches from the write-side DB or relies on individual message events.
    # Here we just update the session counter.
    async with async_session_factory() as session:
        await session.execute(
            update(ChatSessionReadModel)
            .where(ChatSessionReadModel.id == uuid.UUID(payload["session_id"]))
            .values(message_count=ChatSessionReadModel.message_count + payload["count"])
        )
        await session.commit()


_HANDLERS = {
    "chat.message.created": _upsert_message,
    "chat.message.deleted": _soft_delete_message,
    "chat.bulk.messages.created": _upsert_bulk_messages,
}


async def run_consumer() -> None:
    consumer = AIOKafkaConsumer(
        settings.topic_chat_events,
        settings.topic_chat_bulk,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.kafka_consumer_group,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda v: json.loads(v.decode()),
    )
    await consumer.start()
    logger.info("Chat query projector consumer started")
    try:
        async for msg in consumer:
            event_type = msg.value.get("event_type")
            handler = _HANDLERS.get(event_type)
            if handler:
                try:
                    await handler(msg.value)
                except Exception as exc:
                    logger.error("Failed to project event %s: %s", event_type, exc)
            else:
                logger.warning("Unknown event type: %s", event_type)
    finally:
        await consumer.stop()
        logger.info("Chat query projector consumer stopped")
