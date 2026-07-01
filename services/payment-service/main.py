from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.common.exceptions import register_exception_handlers
from app.common.health import router as health_router
from app.common.logging import setup_logging
from app.config import settings

_TAGS = [
    {
        "name": "payments",
        "description": (
            "Payment processing endpoints (Stripe integration). "
            "Currently returns a stub response — wire up `app/payments/service.py` to enable."
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
    title="Payment Service",
    version="1.0.0",
    description=(
        "Handles payment processing via Stripe. "
        "The Stripe integration is not yet configured — see `app/payments/service.py`. "
        "All endpoints require a valid JWT (Bearer token or `access_token` cookie)."
    ),
    openapi_tags=_TAGS,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

register_exception_handlers(app)

from app.payments.router import router as payments_router

app.include_router(health_router)
app.include_router(payments_router)


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
            "description": "JWT access token from `POST /api/auth/login`.",
        },
        "CookieAuth": {
            "type": "apiKey",
            "in": "cookie",
            "name": "access_token",
            "description": "HTTP-only cookie set by `POST /api/auth/login`.",
        },
    }
    schema["security"] = [{"BearerAuth": []}, {"CookieAuth": []}]
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = _custom_openapi
