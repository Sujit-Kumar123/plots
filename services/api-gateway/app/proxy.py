"""Proxy utility — forwards requests to downstream microservices with retry."""
import asyncio
import logging

import httpx
from fastapi import Request, Response
from fastapi.responses import JSONResponse

from app.config import settings

logger = logging.getLogger(__name__)
_RETRY_STATUSES = {502, 503, 504}

# Headers that httpx/Starlette manage themselves — strip them from upstream responses
# so we don't end up with duplicates or stale values.
_SKIP_RESPONSE_HEADERS = {"content-length", "transfer-encoding", "set-cookie"}


def _build_response(resp: httpx.Response) -> Response:
    """Convert an httpx response to a Starlette Response, preserving all Set-Cookie headers."""
    # Build a plain-dict of headers, skipping the ones we handle manually
    headers = {
        k: v for k, v in resp.headers.items()
        if k.lower() not in _SKIP_RESPONSE_HEADERS
    }
    response = Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=headers,
        media_type=resp.headers.get("content-type"),
    )
    # Forward every Set-Cookie header individually.
    # dict(resp.headers) collapses duplicate keys so we must use get_list().
    for cookie in resp.headers.get_list("set-cookie"):
        response.raw_headers.append((b"set-cookie", cookie.encode("latin-1")))
    return response


async def proxy(request: Request, base_url: str, path: str) -> Response:
    """Forward a request to base_url + path, retrying on 5xx errors."""
    client: httpx.AsyncClient = request.app.state.http_client
    url = f"{base_url}{path}"
    method = request.method
    body = await request.body()
    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in {"host", "content-length", "transfer-encoding"}
    }
    if hasattr(request.state, "user_id") and request.state.user_id:
        headers["x-user-id"] = str(request.state.user_id)
    if hasattr(request.state, "user_payload") and request.state.user_payload:
        payload = request.state.user_payload
        if "role" in payload:
            headers["x-user-role"] = str(payload["role"])
        if "email" in payload:
            headers["x-user-email"] = str(payload["email"])
    if hasattr(request.state, "request_id"):
        headers["x-request-id"] = request.state.request_id
    if settings.internal_service_secret:
        headers["x-internal-secret"] = settings.internal_service_secret

    last_exc: Exception | None = None
    for attempt in range(1, settings.proxy_max_retries + 1):
        try:
            resp = await client.request(
                method=method,
                url=url,
                content=body,
                headers=headers,
                params=dict(request.query_params),
            )
            if resp.status_code not in _RETRY_STATUSES:
                return _build_response(resp)
            logger.warning(
                "Downstream %d on attempt %d/%d for %s %s",
                resp.status_code, attempt, settings.proxy_max_retries, method, url,
            )
            if attempt < settings.proxy_max_retries:
                await asyncio.sleep(0.3 * attempt)
                continue
            return _build_response(resp)
        except (httpx.TimeoutException, httpx.ConnectError) as exc:
            last_exc = exc
            logger.warning(
                "Downstream error attempt %d/%d for %s %s: %s",
                attempt, settings.proxy_max_retries, method, url, exc,
            )
            if attempt < settings.proxy_max_retries:
                await asyncio.sleep(0.5 * attempt)

    logger.error("All %d proxy attempts failed for %s %s", settings.proxy_max_retries, method, url)
    return JSONResponse(
        status_code=503,
        content={"detail": "Service temporarily unavailable. Please retry."},
        headers={"Retry-After": "5"},
    )
