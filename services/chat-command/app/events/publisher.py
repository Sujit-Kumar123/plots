"""Kafka producer — publishes domain events after successful writes."""
import json
import logging
from typing import Any

from aiokafka import AIOKafkaProducer

from app.config import settings

logger = logging.getLogger(__name__)

_producer: AIOKafkaProducer | None = None


async def start_producer() -> None:
    global _producer
    _producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        acks=settings.kafka_producer_acks,
        enable_idempotence=True,
        value_serializer=lambda v: json.dumps(v, default=str).encode(),
        key_serializer=lambda k: k.encode() if k else None,
    )
    await _producer.start()
    logger.info("Kafka producer started")


async def stop_producer() -> None:
    if _producer:
        await _producer.stop()
        logger.info("Kafka producer stopped")


async def publish(topic: str, event: Any, key: str | None = None) -> None:
    """Publish a Pydantic model (or dict) to a Kafka topic."""
    if _producer is None:
        raise RuntimeError("Kafka producer not initialised")

    payload = event.model_dump() if hasattr(event, "model_dump") else event
    await _producer.send_and_wait(topic, value=payload, key=key)
    logger.debug("Published event to %s key=%s", topic, key)
