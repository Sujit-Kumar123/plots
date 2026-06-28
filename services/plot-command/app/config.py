from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Plot Command Service"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://mvp_user:mvp_pass@postgres:5432/mvp_db"
    db_pool_size: int = 10
    db_max_overflow: int = 20

    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_producer_acks: str = "all"

    topic_plot_events: str = "plot.events"
    topic_plot_bulk: str = "plot.bulk.commands"

    # Max elements allowed in a single plot (guard against oversized payloads)
    max_plot_elements: int = 10_000


settings = Settings()
