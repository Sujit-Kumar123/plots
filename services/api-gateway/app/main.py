from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.middleware import JWTAuthMiddleware
from app.routers import chat, plot


@asynccontextmanager
async def lifespan(app: FastAPI):
    limits = httpx.Limits(max_connections=200, max_keepalive_connections=50)
    timeout = httpx.Timeout(
        connect=settings.proxy_connect_timeout,
        read=settings.proxy_read_timeout,
        write=settings.proxy_read_timeout,
        pool=settings.proxy_connect_timeout,
    )
    app.state.http_client = httpx.AsyncClient(limits=limits, timeout=timeout)
    yield
    await app.state.http_client.aclose()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)
app.add_middleware(JWTAuthMiddleware)

app.include_router(chat.router, prefix="/api/v1/chat")
app.include_router(plot.router, prefix="/api/v1/plots")


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "service": "api-gateway"}


@app.get("/health/ready", tags=["health"])
async def readiness(request: Request):
    client: httpx.AsyncClient = request.app.state.http_client
    checks = {}
    for name, url in [
        ("chat-command", f"{settings.chat_command_url}/health"),
        ("chat-query", f"{settings.chat_query_url}/health"),
        ("plot-command", f"{settings.plot_command_url}/health"),
        ("plot-query", f"{settings.plot_query_url}/health"),
    ]:
        try:
            resp = await client.get(url, timeout=3.0)
            checks[name] = "ok" if resp.status_code == 200 else "degraded"
        except Exception:
            checks[name] = "error"
    all_ok = all(v == "ok" for v in checks.values())
    return JSONResponse(
        status_code=200 if all_ok else 503,
        content={"status": "ready" if all_ok else "degraded", "services": checks},
    )
