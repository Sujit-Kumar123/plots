"""Command handlers — orchestrate DB write + Kafka publish."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.commands.schemas import (
    BulkCreateChatMessagesCommand,
    CreateChatMessageCommand,
    DeleteChatMessageCommand,
)
from app.config import settings
from app.events import publisher
from app.events.schemas import (
    ChatBulkMessagesCreatedEvent,
    ChatMessageCreatedEvent,
    ChatMessageDeletedEvent,
)
from app.models import ChatMessage, ChatSession


async def handle_create_message(
    cmd: CreateChatMessageCommand, user_id: uuid.UUID, db: AsyncSession
) -> ChatMessage:
    message = ChatMessage(
        session_id=cmd.session_id,
        user_id=user_id,
        role=cmd.role,
        content=cmd.content,
        model=cmd.model,
        token_count=cmd.token_count,
    )
    db.add(message)
    await db.flush()  # get generated id before publish

    await db.execute(
        update(ChatSession)
        .where(ChatSession.id == cmd.session_id)
        .values(message_count=ChatSession.message_count + 1)
    )

    event = ChatMessageCreatedEvent(
        message_id=message.id,
        session_id=message.session_id,
        user_id=user_id,
        role=message.role,
        content=message.content,
        model=message.model,
        token_count=message.token_count,
        created_at=message.created_at,
    )
    await publisher.publish(settings.topic_chat_events, event, key=str(cmd.session_id))
    return message


async def handle_bulk_create_messages(
    cmd: BulkCreateChatMessagesCommand, user_id: uuid.UUID, db: AsyncSession
) -> list[uuid.UUID]:
    messages = [
        ChatMessage(
            session_id=cmd.session_id,
            user_id=user_id,
            role=m.role,
            content=m.content,
            model=m.model,
            token_count=m.token_count,
        )
        for m in cmd.messages
    ]
    db.add_all(messages)
    await db.flush()

    await db.execute(
        update(ChatSession)
        .where(ChatSession.id == cmd.session_id)
        .values(message_count=ChatSession.message_count + len(messages))
    )

    ids = [m.id for m in messages]
    event = ChatBulkMessagesCreatedEvent(
        session_id=cmd.session_id,
        user_id=user_id,
        message_ids=ids,
        count=len(ids),
        created_at=datetime.now(timezone.utc),
    )
    await publisher.publish(settings.topic_chat_bulk, event, key=str(cmd.session_id))
    return ids


async def handle_delete_message(
    cmd: DeleteChatMessageCommand, user_id: uuid.UUID, db: AsyncSession
) -> None:
    result = await db.execute(
        select(ChatMessage).where(
            ChatMessage.id == cmd.message_id,
            ChatMessage.user_id == user_id,
            ChatMessage.is_deleted.is_(False),
        )
    )
    message = result.scalar_one_or_none()
    if not message:
        return

    message.is_deleted = True
    await db.flush()

    event = ChatMessageDeletedEvent(
        message_id=cmd.message_id,
        user_id=user_id,
        deleted_at=datetime.now(timezone.utc),
    )
    await publisher.publish(settings.topic_chat_events, event, key=str(message.session_id))
