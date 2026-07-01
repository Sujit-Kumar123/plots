from pathlib import Path

from pydantic_settings import BaseSettings

from .app_config import AppConfig
from .auth_config import AuthConfig
from .azure_auth_config import AzureAuthConfig
from .database_config import DatabaseConfig
from .email_config import EmailConfig
from .google_auth_config import GoogleAuthConfig

# Resolve the service root (.env lives next to pyproject.toml):
#   services/auth-service/app/config/__init__.py → parents[2] = services/auth-service/
#   /app/app/config/__init__.py (Docker WORKDIR=/app)  → parents[2] = /app
_SERVICE_ROOT = Path(__file__).parents[2]


class Settings(
    AppConfig,
    DatabaseConfig,
    AuthConfig,
    GoogleAuthConfig,
    AzureAuthConfig,
    EmailConfig,
    BaseSettings,
):
    model_config = {
        "env_file": str(_SERVICE_ROOT / ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
