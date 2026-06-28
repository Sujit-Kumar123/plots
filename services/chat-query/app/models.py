"""Read-side (query) models — denormalised for fast lookups."""
import uuid

from sqlalchemy import Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ChatMessageReadModel(Base):
    """Flat projection of a chat message — optimised for read patterns."""
    __tablename__ = "chat_messages"
    __table_args__ = (
        Index("ix_chat_msg_session", "session_id"),
        Index("ix_chat_msg_user", "user_id"),
        {"schema": "chat_read"},
    )

    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str | None] = mapped_column(String(64), nullable=True)
    token_count: Mapped[int | None] = mapped_column(nullable=True)


class ChatSessionReadModel(Base):
    """Flat projection of a chat session with denormalised stats."""
    __tablename__ = "chat_sessions"
    __table_args__ = (
        Index("ix_chat_session_user", "user_id"),
        {"schema": "chat_read"},
    )

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="New Chat")
    message_count: Mapped[int] = mapped_column(nullable=False, default=0)
    last_message_preview: Mapped[str | None] = mapped_column(String(200), nullable=True)
