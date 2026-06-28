import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.queries.handlers import get_message, get_session_messages, list_sessions

router = APIRouter()


def _user_id(x_user_id: str = Header(...)) -> uuid.UUID:
    try:
        return uuid.UUID(x_user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid X-User-ID header")


@router.get("/sessions")
async def get_sessions(
    user_id: uuid.UUID = Depends(_user_id),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await list_sessions(user_id, db, limit, offset)


@router.get("/sessions/{session_id}/messages")
async def get_messages(
    session_id: uuid.UUID,
    user_id: uuid.UUID = Depends(_user_id),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await get_session_messages(session_id, user_id, db, limit, offset)


@router.get("/messages/{message_id}")
async def get_single_message(
    message_id: uuid.UUID,
    user_id: uuid.UUID = Depends(_user_id),
    db: AsyncSession = Depends(get_db),
):
    msg = await get_message(message_id, user_id, db)
    if not msg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    return msg
