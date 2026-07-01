from pydantic_settings import BaseSettings


class AuthConfig(BaseSettings):
    secret_key: str = "change-me-to-a-random-string"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Auth method toggles — set in .env to enable/disable each provider
    auth_email_enabled: bool = True
    auth_google_enabled: bool = False
    auth_azure_enabled: bool = False
