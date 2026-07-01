import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from app.common.exceptions import register_exception_handlers
from app.common.internal_auth import InternalAuthMiddleware
from app.common.logging import setup_logging
from app.config import settings
from app.database import check_db_health, engine
from app.events.publisher import is_producer_ready, start_producer, stop_producer
from app.projections.consumer import is_consumer_healthy, run_consumer
from app.routers.chat import router

_TAGS = [
    {
        "name": "messages",
        "description": "Create, retrieve, and delete individual chat messages.",
    },
    {
        "name": "sessions",
        "description": (
            "List chat sessions and fetch their messages. "
            "Sessions are auto-created on the first message — no explicit session-create call needed."
        ),
    },
]


def _run_migrations() -> None:
    from alembic import command
    from alembic.config import Config
    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(debug=settings.debug)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _run_migrations)
    await start_producer()
    consumer_task = asyncio.create_task(run_consumer())
    app.state.consumer_task = consumer_task
    yield
    consumer_task.cancel()
    try:
        await asyncio.wait_for(consumer_task, timeout=15.0)
    except (asyncio.CancelledError, asyncio.TimeoutError):
        pass
    await stop_producer()
    await engine.dispose()


app = FastAPI(
    title="Chat Service",
    version="1.0.0",
    description=(
        "CQRS chat microservice. Handles message persistence (write side) and "
        "session/message retrieval (read side). Sessions are created automatically on the "
        "first message. All requests must include the `x-internal-secret` header — this "
        "is injected by the API Gateway and must not be called directly from the browser."
    ),
    openapi_tags=_TAGS,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

app.add_middleware(InternalAuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["X-User-ID", "X-Request-ID", "Content-Type"],
)

register_exception_handlers(app)
app.include_router(router)


@app.get("/health", tags=["health"], summary="Liveness probe")
async def health():
    return {"status": "ok", "service": "chat-service"}


@app.get("/health/ready", tags=["health"], summary="Readiness probe")
async def readiness():
    db_ok = await check_db_health()
    producer_ok = is_producer_ready()
    consumer_ok = is_consumer_healthy()
    if db_ok and producer_ok and consumer_ok:
        return {"status": "ready", "db": "ok", "kafka_producer": "ok", "kafka_consumer": "ok"}
    return JSONResponse(
        status_code=503,
        content={
            "status": "not_ready",
            "db": "ok" if db_ok else "error",
            "kafka_producer": "ok" if producer_ok else "error",
            "kafka_consumer": "ok" if consumer_ok else "error",
        },
    )


def _custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
    )
    schema.setdefault("components", {})["securitySchemes"] = {
        "InternalSecret": {
            "type": "apiKey",
            "in": "header",
            "name": "x-internal-secret",
            "description": "Shared secret for service-to-service calls (injected by api-gateway).",
        },
        "UserID": {
            "type": "apiKey",
            "in": "header",
            "name": "x-user-id",
            "description": "Authenticated user UUID (injected by api-gateway after JWT validation).",
        },
    }
    schema["security"] = [{"InternalSecret": [], "UserID": []}]
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = _custom_openapi
