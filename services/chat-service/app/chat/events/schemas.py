"""Domain event schemas published to Kafka after successful commands."""
import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class ChatMessageCreatedEvent(BaseModel):
    event_type: Literal["chat.message.created"] = "chat.message.created"
    message_id: uuid.UUID
    session_id: uuid.UUID
    user_id: uuid.UUID
    role: str
    content: str
    model: str | None
    token_count: int | None
    created_at: datetime


class ChatBulkMessagesCreatedEvent(BaseModel):
    event_type: Literal["chat.bulk.messages.created"] = "chat.bulk.messages.created"
    session_id: uuid.UUID
    user_id: uuid.UUID
    message_ids: list[uuid.UUID]
    count: int
    created_at: datetime


class ChatMessageDeletedEvent(BaseModel):
    event_type: Literal["chat.message.deleted"] = "chat.message.deleted"
    message_id: uuid.UUID
    user_id: uuid.UUID
    deleted_at: datetime
