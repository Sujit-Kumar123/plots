import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.auth.middlewares import SessionValidationMiddleware
from app.common.exceptions import register_exception_handlers
from app.common.health import router as health_router
from app.common.logging import setup_logging
from app.common.middleware import RateLimitMiddleware, RequestIDMiddleware, RequestLoggingMiddleware
from app.config import settings

logger = logging.getLogger(__name__)

_TAGS_METADATA = [
    {"name": "auth", "description": "Register, login, logout, password reset, token refresh"},
    {"name": "google-auth", "description": "Google OAuth2 sign-in and account linking"},
    {"name": "azure-auth", "description": "Azure AD OAuth2 sign-in and account linking"},
    {"name": "profile", "description": "User profile read and update"},
    {"name": "roles", "description": "Role CRUD and user role assignment"},
    {"name": "permissions", "description": "Permission CRUD and role-permission assignment"},
    {"name": "admin", "description": "Admin-only user management"},
    {"name": "audit", "description": "Audit log access"},
    {"name": "notifications", "description": "In-app notifications"},
    {"name": "uploads", "description": "File upload and management"},
    {"name": "payments", "description": "Payment processing"},
    {"name": "health", "description": "Service health check"},
    {"name": "plot", "description": "Plot sheet save and load"},
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(debug=settings.debug)
    _log_auth_methods()
    yield


def _log_auth_methods() -> None:
    active = []
    if settings.auth_email_enabled:
        active.append("email/password")
    if settings.auth_google_enabled:
        active.append("Google OAuth")
    if settings.auth_azure_enabled:
        active.append("Azure AD OAuth")

    if active:
        logger.info("Auth methods enabled: %s", ", ".join(active))
    else:
        logger.warning(
            "No auth methods are enabled — set AUTH_EMAIL_ENABLED, AUTH_GOOGLE_ENABLED, or AUTH_AZURE_ENABLED in .env"
        )


def _custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title="MVP Backend API",
        version="1.0.0",
        description=(
            "REST API for the MVP platform.\n\n"
            "**Authentication:** Use the `Authorize` button to set a Bearer token, "
            "or log in via `/api/auth/login` — tokens are also stored in `httpOnly` cookies "
            "and sent automatically by the browser."
        ),
        routes=app.routes,
        tags=_TAGS_METADATA,
    )

    schema.setdefault("components", {}).setdefault("securitySchemes", {})["BearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "Paste your `access_token` here.",
    }
    schema["security"] = [{"BearerAuth": []}]

    app.openapi_schema = schema
    return schema


def create_app() -> FastAPI:
    app = FastAPI(
        title="MVP Backend API",
        version="1.0.0",
        debug=settings.debug,
        lifespan=lifespan,
        openapi_tags=_TAGS_METADATA,
        swagger_ui_parameters={"persistAuthorization": True},
    )

    app.openapi = lambda: _custom_openapi(app)  # type: ignore[method-assign]

    # Middleware (order matters — outermost first)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(SessionValidationMiddleware)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    register_exception_handlers(app)

    # Routers
    from app.auth.routers.admin_router import router as admin_router
    from app.audit.routers.router import router as audit_router
    from app.auth.routers.auth_route import router as auth_router
    from app.auth.routers.permission_route import router as permission_router
    from app.auth.routers.profile_router import router as profile_router
    from app.auth.routers.role_route import router as role_router
    from app.notifications.router import router as notifications_router
    from app.payments.router import router as payments_router
    from app.plot.routers import router as plot_router
    from app.uploads.router import router as uploads_router

    app.include_router(health_router)
    app.include_router(auth_router)  # always — contains /refresh and /logout
    app.include_router(profile_router)
    app.include_router(role_router)
    app.include_router(permission_router)
    app.include_router(admin_router)
    app.include_router(audit_router)
    app.include_router(notifications_router)
    app.include_router(uploads_router)
    app.include_router(payments_router)
    app.include_router(plot_router)

    # SSO routers — only registered when the provider is enabled and configured
    if settings.auth_google_enabled and settings.google_client_id:
        from app.auth.routers.google_router import router as google_router

        app.include_router(google_router)

    if settings.auth_azure_enabled and settings.azure_client_id:
        from app.auth.routers.azure_router import router as azure_router

        app.include_router(azure_router)

    return app


app = create_app()
