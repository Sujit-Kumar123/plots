from pathlib import Path

from pydantic_settings import BaseSettings

from .app_config import AppConfig
from .auth_config import AuthConfig
from .azure_auth_config import AzureAuthConfig
from .database_config import DatabaseConfig
from .email_config import EmailConfig
from .google_auth_config import GoogleAuthConfig

# Resolve the monorepo root regardless of where the process is started from:
#   backend/app/config/__init__.py → parents[3] = project root (local)
#   /app/backend/app/config/__init__.py → parents[3] = /app (Docker)
_ROOT_ENV = Path(__file__).parents[3] / ".env"


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
        "env_file": str(_ROOT_ENV),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
