from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    database_url: str = "postgresql+asyncpg://mvp_user:mvp_pass@postgres:5432/mvp_db"
    db_pool_size: int = 10
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800
