from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from app.audit.middleware import AuditMiddleware
from app.audit.router import router as audit_admin_router
from app.common.exceptions import register_exception_handlers
from app.common.logging import setup_logging
from app.common.middleware import RateLimitMiddleware, RequestIDMiddleware, RequestLoggingMiddleware
from app.config import settings
from app.database import engine
from app.middleware import SessionValidationMiddleware
from app.routers import chat, plot
from app.routers.backend import (
    admin_router,
    auth_router,
    notification_router,
    payment_router,
    profile_router,
    uploads_router,
)

_TAGS = [
    {
        "name": "auth",
        "description": (
            "Proxy to auth-service. Register, login, logout, password management, and OAuth flows. "
            "Public endpoints do not require a token."
        ),
    },
    {
        "name": "profile",
        "description": "Proxy to auth-service. Read and update the authenticated user's profile.",
    },
    {
        "name": "admin",
        "description": "Proxy to auth-service. User management for admins. Requires `users:*` permissions.",
    },
    {
        "name": "roles",
        "description": "Proxy to auth-service. Role management. Requires `roles:*` permissions.",
    },
    {
        "name": "permissions",
        "description": "Proxy to auth-service. Permission management. Requires `permissions:*` permissions.",
    },
    {
        "name": "chat",
        "description": (
            "CQRS chat endpoints — proxied to chat-service. "
            "All `/api/v1/chat/*` routes require a valid JWT."
        ),
    },
    {
        "name": "plots",
        "description": (
            "CQRS plot (sheet) endpoints — proxied to plot-service. "
            "All `/api/v1/plots/*` routes require a valid JWT."
        ),
    },
    {
        "name": "payments",
        "description": "Proxy to payment-service (stub — Stripe integration not yet configured).",
    },
    {
        "name": "notifications",
        "description": "Proxy to notification-service. Send email and SMS.",
    },
    {
        "name": "health",
        "description": "Liveness and readiness probes.",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(debug=settings.debug)
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
    await engine.dispose()


app = FastAPI(
    title="API Gateway",
    version="1.0.0",
    description=(
        "Single entry point for the Plots microservices platform. "
        "Validates JWT tokens, injects `x-user-id` / `x-user-role` / `x-user-email` headers, "
        "and reverse-proxies to downstream services. "
        "CQRS routes (`/api/v1/*`) require authentication. "
        "Use the **Authorize** button to set your Bearer token before calling protected endpoints."
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
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)
register_exception_handlers(app)

app.add_middleware(AuditMiddleware)
app.add_middleware(SessionValidationMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RequestIDMiddleware)

# ── CQRS routes ───────────────────────────────────────────────────────────────
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(plot.router, prefix="/api/v1/plots", tags=["plots"])

# ── Backend service proxy routes ──────────────────────────────────────────────
app.include_router(auth_router, prefix="/api/auth")
app.include_router(profile_router, prefix="/api/profile")
app.include_router(audit_admin_router, prefix="/api/admin")
app.include_router(admin_router, prefix="/api/admin")
app.include_router(uploads_router, prefix="/api/uploads")
app.include_router(payment_router, prefix="/api/payments")
app.include_router(notification_router, prefix="/api/notifications")


@app.get("/health", tags=["health"], summary="Liveness probe")
async def health():
    return {"status": "ok", "service": "api-gateway"}


@app.get("/health/ready", tags=["health"], summary="Readiness probe",
         description="Checks connectivity to all downstream microservices.")
async def readiness(request: Request):
    client: httpx.AsyncClient = request.app.state.http_client
    checks = {}
    for name, url in [
        ("chat-service", f"{settings.chat_command_url}/health/ready"),
        ("plot-service", f"{settings.plot_command_url}/health/ready"),
        ("auth-service", f"{settings.auth_service_url}/health/ready"),
        ("payment-service", f"{settings.payment_service_url}/health/ready"),
        ("notification-service", f"{settings.notification_service_url}/health/ready"),
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
            "description": (
                "JWT access token. Obtain from `POST /api/auth/login`, "
                "then click **Authorize** and paste the token."
            ),
        },
        "CookieAuth": {
            "type": "apiKey",
            "in": "cookie",
            "name": "access_token",
            "description": "HTTP-only cookie set automatically by `POST /api/auth/login`.",
        },
    }
    schema["security"] = [{"BearerAuth": []}, {"CookieAuth": []}]
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = _custom_openapi
