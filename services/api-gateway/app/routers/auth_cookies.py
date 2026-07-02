"""Dedicated auth routes that set / clear HttpOnly cookies in the gateway.

The generic auth_router proxies everything to auth-service, but cookies set
by auth-service cannot reliably survive the proxy chain.  These explicit
handlers intercept the four cookie-producing endpoints, parse the token
payload from the upstream JSON body, and call set_cookie() directly on the
JSONResponse that is returned — the only approach that is guaranteed to work
regardless of Starlette/FastAPI version or middleware ordering.

Registered BEFORE auth_router in main.py so FastAPI matches these first.
"""

import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.proxy import proxy

router = APIRouter(tags=["auth"])

_SECURE = not settings.debug  # True in prod (debug=False), False in dev
_ACCESS_MAX_AGE  = 30 * 60           # 30 minutes — must match auth-service AuthConfig
_REFRESH_MAX_AGE = 7 * 24 * 60 * 60  # 7 days


def _parse_body(upstream_body: bytes) -> dict:
    try:
        return json.loads(upstream_body)
    except Exception:
        return {}


def _make_response(upstream) -> JSONResponse:
    content = _parse_body(upstream.body)
    # Exclude Set-Cookie / content-length / content-type from upstream headers
    headers = {
        k: v for k, v in upstream.headers.items()
        if k.lower() not in ("set-cookie", "content-length", "content-type")
    }
    return JSONResponse(
        content=content,
        status_code=upstream.status_code,
        headers=headers,
    )


def _set_tokens(result: JSONResponse, content: dict) -> None:
    tokens = content.get("data", {}).get("tokens", {})
    access_token  = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    if access_token and refresh_token:
        result.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=_SECURE,
            samesite="lax",
            max_age=_ACCESS_MAX_AGE,
            path="/",
        )
        result.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=_SECURE,
            samesite="lax",
            max_age=_REFRESH_MAX_AGE,
            path="/",
        )


def _set_tokens_refresh(result: JSONResponse, content: dict) -> None:
    """Refresh endpoint returns tokens directly under data, not under data.tokens."""
    tokens = content.get("data", {})
    access_token  = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    if access_token and refresh_token:
        result.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=_SECURE,
            samesite="lax",
            max_age=_ACCESS_MAX_AGE,
            path="/",
        )
        result.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=_SECURE,
            samesite="lax",
            max_age=_REFRESH_MAX_AGE,
            path="/",
        )


def _clear_cookies(result: JSONResponse) -> None:
    result.delete_cookie("access_token",  path="/")
    result.delete_cookie("refresh_token", path="/")


@router.post("/login")
async def login(request: Request) -> JSONResponse:
    upstream = await proxy(request, settings.auth_service_url, request.url.path)
    result = _make_response(upstream)
    if upstream.status_code == 200:
        _set_tokens(result, _parse_body(upstream.body))
    return result


@router.post("/register")
async def register(request: Request) -> JSONResponse:
    upstream = await proxy(request, settings.auth_service_url, request.url.path)
    result = _make_response(upstream)
    if upstream.status_code == 200:
        _set_tokens(result, _parse_body(upstream.body))
    return result


@router.post("/refresh")
async def refresh(request: Request) -> JSONResponse:
    upstream = await proxy(request, settings.auth_service_url, request.url.path)
    result = _make_response(upstream)
    if upstream.status_code == 200:
        _set_tokens_refresh(result, _parse_body(upstream.body))
    return result


@router.post("/logout")
async def logout(request: Request) -> JSONResponse:
    upstream = await proxy(request, settings.auth_service_url, request.url.path)
    result = _make_response(upstream)
    _clear_cookies(result)
    return result
