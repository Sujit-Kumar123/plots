import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.commands.handlers import (
    handle_bulk_create_messages,
    handle_create_message,
    handle_delete_message,
)
from app.commands.schemas import BulkCreateChatMessagesCommand, CreateChatMessageCommand, DeleteChatMessageCommand
from app.database import get_db
from app.queries.handlers import get_message, get_session_messages, list_sessions
from app.schemas import (
    BulkMessagesAcceptedResponse,
    MessageCreatedResponse,
    MessageItem,
    MessageListResponse,
    SessionListResponse,
)

router = APIRouter()

_ERR = {
    400: {"description": "Bad request — invalid UUID or body"},
    401: {"description": "Missing or invalid auth token"},
    403: {"description": "Forbidden — invalid internal secret"},
    404: {"description": "Resource not found"},
    422: {"description": "Validation error"},
}


def _user_id(x_user_id: str = Header(..., description="UUID of the authenticated user (injected by gateway)")) -> uuid.UUID:
    try:
        return uuid.UUID(x_user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid X-User-ID header")


# ── Command endpoints ─────────────────────────────────────────────────────────

@router.post(
    "/messages",
    status_code=201,
    response_model=MessageCreatedResponse,
    summary="Save a chat message",
    description=(
        "Persists a single chat message (user or assistant turn) to the write model. "
        "Automatically creates the session on first message. "
        "Publishes a `chat.message.created` event to Kafka."
    ),
    responses={**_ERR},
    tags=["messages"],
)
async def create_message(
    cmd: CreateChatMessageCommand,
    user_id: uuid.UUID = Depends(_user_id),
    db: AsyncSession = Depends(get_db),
):
    message = await handle_create_message(cmd, user_id, db)
    return {"id": str(message.id), "session_id": str(message.session_id)}


@router.post(
    "/messages/bulk",
    status_code=202,
    response_model=BulkMessagesAcceptedResponse,
    summary="Bulk-save chat messages",
    description=(
        "Accepts up to 1 000 messages for a single session in one request. "
        "Returns 202 immediately; messages are persisted and projected asynchronously via Kafka."
    ),
    responses={**_ERR},
    tags=["messages"],
)
async def create_messages_bulk(
    cmd: BulkCreateChatMessagesCommand,
    user_id: uuid.UUID = Depends(_user_id),
    db: AsyncSession = Depends(get_db),
):
    ids = await handle_bulk_create_messages(cmd, user_id, db)
    return {"accepted": len(ids), "ids": [str(i) for i in ids]}


@router.delete(
    "/messages/{message_id}",
    status_code=204,
    summary="Soft-delete a message",
    description="Marks a message as deleted. The row is retained for audit purposes.",
    responses={**_ERR},
    tags=["messages"],
)
async def delete_message(
    message_id: uuid.UUID,
    user_id: uuid.UUID = Depends(_user_id),
    db: AsyncSession = Depends(get_db),
):
    await handle_delete_message(DeleteChatMessageCommand(message_id=message_id), user_id, db)


# ── Query endpoints ───────────────────────────────────────────────────────────

@router.get(
    "/sessions",
    response_model=SessionListResponse,
    summary="List chat sessions",
    description=(
        "Returns a paginated list of the authenticated user's chat sessions, "
        "ordered by most recently updated."
    ),
    responses={**_ERR},
    tags=["sessions"],
)
async def get_sessions(
    user_id: uuid.UUID = Depends(_user_id),
    limit: int = Query(default=20, le=100, description="Maximum items to return"),
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
    db: AsyncSession = Depends(get_db),
):
    return await list_sessions(user_id, db, limit, offset)


@router.get(
    "/sessions/{session_id}/messages",
    response_model=MessageListResponse,
    summary="Get messages for a session",
    description="Returns all messages in a session, ordered chronologically (oldest first).",
    responses={**_ERR},
    tags=["sessions"],
)
async def get_messages(
    session_id: uuid.UUID,
    user_id: uuid.UUID = Depends(_user_id),
    limit: int = Query(default=50, le=200, description="Maximum items to return"),
    offset: int = Query(default=0, ge=0, description="Number of items to skip"),
    db: AsyncSession = Depends(get_db),
):
    return await get_session_messages(session_id, user_id, db, limit, offset)


@router.get(
    "/messages/{message_id}",
    response_model=MessageItem,
    summary="Get a single message",
    description="Fetches a single message by its UUID.",
    responses={**_ERR},
    tags=["messages"],
)
async def get_single_message(
    message_id: uuid.UUID,
    user_id: uuid.UUID = Depends(_user_id),
    db: AsyncSession = Depends(get_db),
):
    msg = await get_message(message_id, user_id, db)
    if not msg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    return msg
