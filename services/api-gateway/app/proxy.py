"""Thin reverse-proxy helper — forwards request to a downstream service."""
from fastapi import Request, Response
import httpx


async def proxy(request: Request, base_url: str, path: str) -> Response:
    client: httpx.AsyncClient = request.app.state.http_client
    body = await request.body()

    # Forward original headers except host; inject user identity
    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in ("host", "content-length")
    }
    if hasattr(request.state, "user_id") and request.state.user_id:
        headers["X-User-ID"] = str(request.state.user_id)

    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    if request.url.query:
        url = f"{url}?{request.url.query}"

    upstream = await client.request(
        method=request.method,
        url=url,
        content=body,
        headers=headers,
    )

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=dict(upstream.headers),
        media_type=upstream.headers.get("content-type"),
    )
