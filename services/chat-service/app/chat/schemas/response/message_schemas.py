"""Pydantic response schemas for OpenAPI / Swagger documentation."""
from pydantic import BaseModel


class MessageCreatedResponse(BaseModel):
    id: str
    session_id: str


class BulkMessagesAcceptedResponse(BaseModel):
    accepted: int
    ids: list[str]


class MessageItem(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    model: str | None
    token_count: int | None
    created_at: str


class MessageListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[MessageItem]


class SessionItem(BaseModel):
    id: str
    title: str
    message_count: int
    last_message_preview: str | None
    updated_at: str


class SessionListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[SessionItem]
