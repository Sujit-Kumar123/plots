from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.common.exceptions import register_exception_handlers
from app.common.health import router as health_router
from app.common.logging import setup_logging
from app.config import settings
from app.email.router import router as email_router
from app.notifications.router import router as notifications_router

_TAGS = [
    {
        "name": "email",
        "description": (
            "Internal email endpoints (SendGrid). Require the `x-internal-secret` header — "
            "called by auth-service and other backend services, **not** directly from the browser."
        ),
    },
    {
        "name": "notifications",
        "description": (
            "User-facing notification endpoints (email, SMS). "
            "Proxied through the API Gateway and require a valid JWT."
        ),
    },
    {
        "name": "health",
        "description": "Liveness probe.",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(debug=settings.debug)
    yield


app = FastAPI(
    title="Notification Service",
    version="1.0.0",
    description=(
        "Sends transactional emails (SendGrid) and SMS (Twilio). "
        "Internal `/api/email/*` endpoints require the `x-internal-secret` header. "
        "User-facing `/api/notifications/*` endpoints require a valid JWT."
    ),
    openapi_tags=_TAGS,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "x-internal-secret"],
)

register_exception_handlers(app)

app.include_router(health_router)
app.include_router(email_router)
app.include_router(notifications_router)


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
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT access token for user-facing `/api/notifications/*` endpoints.",
        },
        "CookieAuth": {
            "type": "apiKey",
            "in": "cookie",
            "name": "access_token",
            "description": "HTTP-only cookie set by `POST /api/auth/login`.",
        },
        "InternalSecret": {
            "type": "apiKey",
            "in": "header",
            "name": "x-internal-secret",
            "description": "Shared secret for internal `/api/email/*` endpoints.",
        },
    }
    schema["security"] = [{"BearerAuth": []}, {"CookieAuth": []}]
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = _custom_openapi
