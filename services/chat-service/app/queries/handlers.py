"""Query handlers — reads write models directly for immediate consistency."""
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.write_models import ChatMessage, ChatSession


async def get_session_messages(
    session_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    count_q = await db.execute(
        select(func.count()).where(
            ChatMessage.session_id == session_id,
            ChatMessage.user_id == user_id,
            ChatMessage.is_deleted.is_(False),
        )
    )
    total = count_q.scalar_one()

    result = await db.execute(
        select(ChatMessage)
        .where(
            ChatMessage.session_id == session_id,
            ChatMessage.user_id == user_id,
            ChatMessage.is_deleted.is_(False),
        )
        .order_by(ChatMessage.created_at)
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
        select(ChatMessage).where(
            ChatMessage.id == message_id,
            ChatMessage.user_id == user_id,
            ChatMessage.is_deleted.is_(False),
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
            ChatSession.user_id == user_id,
            ChatSession.is_deleted.is_(False),
        )
    )
    total = count_q.scalar_one()

    result = await db.execute(
        select(ChatSession)
        .where(
            ChatSession.user_id == user_id,
            ChatSession.is_deleted.is_(False),
        )
        .order_by(ChatSession.updated_at.desc())
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
                "last_message_preview": None,
                "updated_at": s.updated_at.isoformat(),
            }
            for s in sessions
        ],
    }
