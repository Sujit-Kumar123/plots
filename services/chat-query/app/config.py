from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Chat Query Service"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://mvp_user:mvp_pass@postgres:5432/mvp_db"
    db_pool_size: int = 20
    db_max_overflow: int = 40
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800

    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_consumer_group: str = "chat-query-projector"
    kafka_consumer_max_retries: int = 3
    kafka_consumer_retry_backoff: float = 0.5
    topic_chat_events: str = "chat.events"
    topic_chat_bulk: str = "chat.bulk.commands"

    default_page_size: int = 50
    max_page_size: int = 200


settings = Settings()
