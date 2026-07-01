from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Notification Service"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:3000"]

    # Shared secret for x-internal-secret header
    internal_service_secret: str = ""

    # ── Database ───────────────────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://mvp_user:mvp_pass@postgres:5432/mvp_db"
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800

    # SendGrid
    sendgrid_api_key: str = ""
    from_email: str = "noreply@yourapp.com"

    # Twilio SMS
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""


settings = Settings()
