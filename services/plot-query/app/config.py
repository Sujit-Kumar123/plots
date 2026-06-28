from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Plot Query Service"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://mvp_user:mvp_pass@postgres:5432/mvp_db"
    db_pool_size: int = 20
    db_max_overflow: int = 40

    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_consumer_group: str = "plot-query-projector"
    topic_plot_events: str = "plot.events"
    topic_plot_bulk: str = "plot.bulk.commands"

    default_page_size: int = 20
    max_page_size: int = 100


settings = Settings()
