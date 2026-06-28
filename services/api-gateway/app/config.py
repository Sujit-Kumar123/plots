from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Plots API Gateway"
    debug: bool = False

    chat_command_url: str = "http://chat-command:8001"
    chat_query_url: str = "http://chat-query:8002"
    plot_command_url: str = "http://plot-command:8003"
    plot_query_url: str = "http://plot-query:8004"

    # Required — no default; startup fails loudly if SECRET_KEY is not set in env
    secret_key: str
    algorithm: str = "HS256"

    cors_origins: list[str] = ["http://localhost", "http://localhost:3000"]

    proxy_connect_timeout: float = 5.0
    proxy_read_timeout: float = 60.0
    proxy_max_retries: int = 3


settings = Settings()
