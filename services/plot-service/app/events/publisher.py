"""Kafka producer — publishes domain events after successful writes."""
import asyncio
import json
import logging
from typing import Any

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from app.config import settings

logger = logging.getLogger(__name__)
_producer: AIOKafkaProducer | None = None


class KafkaPublishError(Exception):
    """Raised when event publishing fails after all retries are exhausted."""


async def start_producer() -> None:
    global _producer
    last_exc: Exception | None = None
    for attempt in range(1, 6):
        producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            acks=settings.kafka_producer_acks,
            enable_idempotence=True,
            request_timeout_ms=settings.kafka_request_timeout_ms,
            retry_backoff_ms=settings.kafka_retry_backoff_ms,
            value_serializer=lambda v: json.dumps(v, default=str).encode(),
            key_serializer=lambda k: k.encode() if k else None,
        )
        try:
            await asyncio.wait_for(producer.start(), timeout=15.0)
            _producer = producer
            logger.info("Kafka producer started (attempt %d)", attempt)
            return
        except (asyncio.TimeoutError, KafkaError) as exc:
            last_exc = exc
            logger.warning("Kafka producer attempt %d/5 failed: %s", attempt, exc)
            try:
                await producer.stop()
            except Exception:
                pass
            if attempt < 5:
                await asyncio.sleep(5.0)
    raise RuntimeError(f"Kafka producer failed after 5 attempts: {last_exc}") from last_exc


async def stop_producer() -> None:
    if _producer:
        try:
            await asyncio.wait_for(_producer.stop(), timeout=10.0)
            logger.info("Kafka producer stopped")
        except asyncio.TimeoutError:
            logger.warning("Kafka producer stop timed out — forcing close")


def is_producer_ready() -> bool:
    return _producer is not None


async def publish(topic: str, event: Any, key: str | None = None) -> None:
    if _producer is None:
        raise KafkaPublishError("Kafka producer not initialised")

    payload = event.model_dump() if hasattr(event, "model_dump") else event
    last_exc: Exception | None = None
    for attempt in range(1, settings.kafka_publish_retries + 1):
        try:
            await _producer.send_and_wait(topic, value=payload, key=key)
            logger.debug("Published to %s key=%s (attempt %d)", topic, key, attempt)
            return
        except KafkaError as exc:
            last_exc = exc
            logger.warning(
                "Kafka publish attempt %d/%d failed topic=%s: %s",
                attempt, settings.kafka_publish_retries, topic, exc,
            )
            if attempt < settings.kafka_publish_retries:
                await asyncio.sleep(0.5 * attempt)

    raise KafkaPublishError(
        f"Failed to publish to {topic} after {settings.kafka_publish_retries} attempts"
    ) from last_exc
