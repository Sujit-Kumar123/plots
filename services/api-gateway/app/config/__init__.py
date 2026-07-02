from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Plots API Gateway"
    debug: bool = False

    chat_command_url: str = "http://chat-service:8001"
    chat_query_url: str = "http://chat-service:8001"
    plot_command_url: str = "http://plot-service:8003"
    plot_query_url: str = "http://plot-service:8003"
    auth_service_url: str = "http://auth-service:8010"
    payment_service_url: str = "http://payment-service:8011"
    notification_service_url: str = "http://notification-service:8012"

    # Audit DB — connects to same postgres as auth-service to read/write audit_logs
    database_url: str = "postgresql+asyncpg://mvp_user:mvp_pass@postgres:5432/mvp_db"
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800

    # Required — no defaults; startup fails loudly if unset
    secret_key: str
    redis_url: str = "redis://redis:6379/0"
    algorithm: str = "HS256"

    cors_origins: list[str] = ["http://localhost", "http://localhost:3000"]

    # Rate limiting
    rate_limit_api: str = "300/minute"
    rate_limit_login: str = "5/minute"
    rate_limit_register: str = "3/minute"
    rate_limit_password_reset: str = "3/minute"

    proxy_connect_timeout: float = 5.0
    proxy_read_timeout: float = 60.0
    proxy_max_retries: int = 3

    # Shared secret sent to internal services via x-internal-secret header
    internal_service_secret: str = ""


settings = Settings()
