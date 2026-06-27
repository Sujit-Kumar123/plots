from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    app_name: str = "mvp-backend"
    app_env: str = "development"
    debug: bool = True

    cors_origins: list[str] = ["http://localhost:3000"]
    frontend_url: str = "http://localhost:3000"

    # Global per-IP limit applied to every /api/* endpoint
    rate_limit_api: str = "300/minute"

    # Stricter limits for sensitive auth endpoints
    rate_limit_login: str = "5/minute"
    rate_limit_register: str = "3/minute"
    rate_limit_password_reset: str = "3/minute"
