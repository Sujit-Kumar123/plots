"""Command schemas (input contracts for write operations)."""
import uuid
from typing import Literal

from pydantic import BaseModel, Field


class CreateChatMessageCommand(BaseModel):
    session_id: uuid.UUID
    role: Literal["user", "assistant", "system"]
    content: str = Field(..., min_length=1, max_length=32_000)
    model: str | None = None
    token_count: int | None = None


class BulkCreateChatMessagesCommand(BaseModel):
    session_id: uuid.UUID
    messages: list[CreateChatMessageCommand] = Field(..., min_length=1, max_length=1_000)


class DeleteChatMessageCommand(BaseModel):
    message_id: uuid.UUID
