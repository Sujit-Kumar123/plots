from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Plots API Gateway"
    debug: bool = False

    # Downstream service base URLs (K8s ClusterIP DNS names)
    chat_command_url: str = "http://chat-command:8001"
    chat_query_url: str = "http://chat-query:8002"
    plot_command_url: str = "http://plot-command:8003"
    plot_query_url: str = "http://plot-query:8004"

    # JWT — shared with main backend; gateway only validates, never issues
    secret_key: str = "change-me"
    algorithm: str = "HS256"

    # Proxy timeouts (seconds)
    proxy_connect_timeout: float = 5.0
    proxy_read_timeout: float = 60.0


settings = Settings()
