from fastapi import APIRouter, Request
from fastapi.responses import Response

from app.config import settings
from app.proxy import proxy

router = APIRouter(tags=["chat"])

# ── Write operations → chat-command ──────────────────────────────────────────

@router.post("/messages", status_code=201)
async def create_message(request: Request) -> Response:
    return await proxy(request, settings.chat_command_url, "/messages")


@router.post("/messages/bulk", status_code=202)
async def create_messages_bulk(request: Request) -> Response:
    return await proxy(request, settings.chat_command_url, "/messages/bulk")


@router.delete("/messages/{message_id}")
async def delete_message(message_id: str, request: Request) -> Response:
    return await proxy(request, settings.chat_command_url, f"/messages/{message_id}")


# ── Read operations → chat-query ─────────────────────────────────────────────

@router.get("/sessions")
async def list_sessions(request: Request) -> Response:
    return await proxy(request, settings.chat_query_url, "/sessions")


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(session_id: str, request: Request) -> Response:
    return await proxy(request, settings.chat_query_url, f"/sessions/{session_id}/messages")


@router.get("/messages/{message_id}")
async def get_message(message_id: str, request: Request) -> Response:
    return await proxy(request, settings.chat_query_url, f"/messages/{message_id}")
