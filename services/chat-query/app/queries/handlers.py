"""Query handlers — read-only operations against the read model."""
import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ChatMessageReadModel, ChatSessionReadModel


async def get_session_messages(
    session_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    count_q = await db.execute(
        select(func.count()).where(
            ChatMessageReadModel.session_id == session_id,
            ChatMessageReadModel.user_id == user_id,
            ChatMessageReadModel.is_deleted.is_(False),
        )
    )
    total = count_q.scalar_one()

    result = await db.execute(
        select(ChatMessageReadModel)
        .where(
            ChatMessageReadModel.session_id == session_id,
            ChatMessageReadModel.user_id == user_id,
            ChatMessageReadModel.is_deleted.is_(False),
        )
        .order_by(ChatMessageReadModel.created_at)
        .limit(limit)
        .offset(offset)
    )
    messages = result.scalars().all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": [
            {
                "id": str(m.id),
                "session_id": str(m.session_id),
                "role": m.role,
                "content": m.content,
                "model": m.model,
                "token_count": m.token_count,
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ],
    }


async def get_message(message_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession) -> dict | None:
    result = await db.execute(
        select(ChatMessageReadModel).where(
            ChatMessageReadModel.id == message_id,
            ChatMessageReadModel.user_id == user_id,
            ChatMessageReadModel.is_deleted.is_(False),
        )
    )
    m = result.scalar_one_or_none()
    if not m:
        return None
    return {
        "id": str(m.id),
        "session_id": str(m.session_id),
        "role": m.role,
        "content": m.content,
        "model": m.model,
        "token_count": m.token_count,
        "created_at": m.created_at.isoformat(),
    }


async def list_sessions(user_id: uuid.UUID, db: AsyncSession, limit: int = 20, offset: int = 0) -> dict:
    count_q = await db.execute(
        select(func.count()).where(
            ChatSessionReadModel.user_id == user_id,
            ChatSessionReadModel.is_deleted.is_(False),
        )
    )
    total = count_q.scalar_one()

    result = await db.execute(
        select(ChatSessionReadModel)
        .where(
            ChatSessionReadModel.user_id == user_id,
            ChatSessionReadModel.is_deleted.is_(False),
        )
        .order_by(ChatSessionReadModel.updated_at.desc())
        .limit(limit)
        .offset(offset)
    )
    sessions = result.scalars().all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": [
            {
                "id": str(s.id),
                "title": s.title,
                "message_count": s.message_count,
                "last_message_preview": s.last_message_preview,
                "updated_at": s.updated_at.isoformat(),
            }
            for s in sessions
        ],
    }
