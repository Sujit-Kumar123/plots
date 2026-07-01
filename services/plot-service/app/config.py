from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Plot Service"
    debug: bool = False

    # ── Database ───────────────────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://mvp_user:mvp_pass@postgres:5432/mvp_db"
    db_pool_size: int = 20
    db_max_overflow: int = 40
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800

    # ── Kafka producer (command side) ──────────────────────────────────────────
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_producer_acks: str = "all"
    kafka_request_timeout_ms: int = 30_000
    kafka_retry_backoff_ms: int = 500
    kafka_publish_retries: int = 3

    # ── Kafka consumer (projection side) ──────────────────────────────────────
    kafka_consumer_group: str = "plot-query-projector"
    kafka_consumer_max_retries: int = 3
    kafka_consumer_retry_backoff: float = 0.5

    # ── Topics ─────────────────────────────────────────────────────────────────
    topic_plot_events: str = "plot.events"
    topic_plot_bulk: str = "plot.bulk.commands"

    # ── Pagination ─────────────────────────────────────────────────────────────
    default_page_size: int = 20
    max_page_size: int = 100

    # ── Domain limits ──────────────────────────────────────────────────────────
    max_plot_elements: int = 10_000

    # ── Internal auth ──────────────────────────────────────────────────────────
    internal_service_secret: str = ""


settings = Settings()
