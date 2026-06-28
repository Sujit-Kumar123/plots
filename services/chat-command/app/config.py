from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Chat Command Service"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://mvp_user:mvp_pass@postgres:5432/mvp_db"
    db_pool_size: int = 10
    db_max_overflow: int = 20

    # Kafka
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_producer_acks: str = "all"         # strongest durability guarantee

    # Topic names
    topic_chat_events: str = "chat.events"
    topic_chat_bulk: str = "chat.bulk.commands"


settings = Settings()
