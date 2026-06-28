import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.commands.handlers import (
    handle_bulk_create_messages,
    handle_create_message,
    handle_delete_message,
)
from app.commands.schemas import BulkCreateChatMessagesCommand, CreateChatMessageCommand, DeleteChatMessageCommand
from app.database import get_db

router = APIRouter()


def _user_id(x_user_id: str = Header(...)) -> uuid.UUID:
    try:
        return uuid.UUID(x_user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid X-User-ID header")


@router.post("/messages", status_code=201)
async def create_message(
    cmd: CreateChatMessageCommand,
    user_id: uuid.UUID = Depends(_user_id),
    db: AsyncSession = Depends(get_db),
):
    message = await handle_create_message(cmd, user_id, db)
    return {"id": str(message.id), "session_id": str(message.session_id)}


@router.post("/messages/bulk", status_code=202)
async def create_messages_bulk(
    cmd: BulkCreateChatMessagesCommand,
    user_id: uuid.UUID = Depends(_user_id),
    db: AsyncSession = Depends(get_db),
):
    ids = await handle_bulk_create_messages(cmd, user_id, db)
    return {"accepted": len(ids), "ids": [str(i) for i in ids]}


@router.delete("/messages/{message_id}", status_code=204)
async def delete_message(
    message_id: uuid.UUID,
    user_id: uuid.UUID = Depends(_user_id),
    db: AsyncSession = Depends(get_db),
):
    await handle_delete_message(DeleteChatMessageCommand(message_id=message_id), user_id, db)
