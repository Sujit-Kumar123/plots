from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from prometheus_fastapi_instrumentator import Instrumentator

from app.common.exceptions import register_exception_handlers
from app.common.responses import ResponseHandler
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
Instrumentator(excluded_handlers=["/health.*", "/metrics"]).instrument(app).expose(app)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_details = exc.errors()
    field_errors = []
    for error in error_details:
        loc = error.get("loc", [])
        msg = error.get("msg", "Invalid value")
        if len(loc) > 1 and loc[0] in ("body", "query", "path"):
            field_name = str(loc[1])
        else:
            field_name = str(loc[-1]) if loc else "unknown"
        field_label = field_name.replace("_", " ").capitalize()
        replacements = ["string", "number", "integer", "boolean", "field", "value"]
        custom_msg = msg.lower()
        for word in replacements:
            if word.lower() in msg.lower():
                custom_msg = custom_msg.replace(word.lower(), field_label)
                break
        field_errors.append({"field": field_name, "message": custom_msg})
    return ResponseHandler.unprocessable_entity(
        message="Please fill all the required fields.", errors=field_errors
    )


from app.payments.routers.payment_router import router as payments_router

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
