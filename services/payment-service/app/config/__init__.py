from pydantic_settings import BaseSettings, SettingsConfigDict

from .database_config import DatabaseConfig


class Settings(DatabaseConfig, BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Payment Service"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:3000"]

    # Shared secret from api-gateway for internal service calls
    internal_service_secret: str = ""


settings = Settings()
