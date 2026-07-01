import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.common.exceptions import register_exception_handlers
from app.common.health import router as health_router
from app.common.logging import setup_logging
from app.config import settings

logger = logging.getLogger(__name__)

_TAGS = [
    {
        "name": "auth",
        "description": (
            "Register, login, logout, token refresh, and password management. "
            "Successful login sets an `access_token` HTTP-only cookie **and** returns tokens in the response body."
        ),
    },
    {
        "name": "profile",
        "description": "Read and update the authenticated user's profile and change password.",
    },
    {
        "name": "roles",
        "description": "Create, update, delete, and assign roles. Requires `roles:read` / `roles:write` / `roles:delete` permissions.",
    },
    {
        "name": "permissions",
        "description": "Create, update, delete, and assign permissions to roles. Requires `permissions:read` / `permissions:write` / `permissions:delete`.",
    },
    {
        "name": "admin",
        "description": "Admin user management — list, update, activate, deactivate, and delete users. Requires `users:read` / `users:write` / `users:delete`.",
    },
    {
        "name": "uploads",
        "description": "Profile photo upload.",
    },
    {
        "name": "health",
        "description": "Liveness and readiness probes.",
    },
    {
        "name": "internal",
        "description": "Internal service-to-service endpoints — not exposed publicly.",
    },
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
            "No auth methods are enabled — set AUTH_EMAIL_ENABLED, AUTH_GOOGLE_ENABLED, "
            "or AUTH_AZURE_ENABLED in .env"
        )


app = FastAPI(
    title="Auth Service",
    version="1.0.0",
    description=(
        "Handles authentication, authorisation, user profiles, roles, and permissions. "
        "Responses are wrapped in `{success, data, message, errors}`. "
        "Use the **Authorize** button to set your Bearer token or `access_token` cookie before calling protected endpoints."
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

from app.audit.router import internal_router as audit_internal_router
from app.auth.routers.admin_router import router as admin_router
from app.auth.routers.auth_route import router as auth_router
from app.auth.routers.permission_route import router as permission_router
from app.auth.routers.profile_router import router as profile_router
from app.auth.routers.role_route import router as role_router
from app.uploads.router import router as uploads_router

app.include_router(health_router)
app.include_router(audit_internal_router)
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(role_router)
app.include_router(permission_router)
app.include_router(admin_router)
app.include_router(uploads_router)

if settings.auth_google_enabled and settings.google_client_id:
    from app.auth.routers.google_router import router as google_router
    app.include_router(google_router)

if settings.auth_azure_enabled and settings.azure_client_id:
    from app.auth.routers.azure_router import router as azure_router
    app.include_router(azure_router)


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
            "description": "JWT access token. Obtain from `POST /api/auth/login`, then paste here.",
        },
        "CookieAuth": {
            "type": "apiKey",
            "in": "cookie",
            "name": "access_token",
            "description": "HTTP-only cookie set automatically by `POST /api/auth/login`.",
        },
    }
    # Apply globally as default; public endpoints (login/register) ignore it
    schema["security"] = [{"BearerAuth": []}, {"CookieAuth": []}]
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = _custom_openapi
