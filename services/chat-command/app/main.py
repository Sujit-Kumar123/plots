import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import engine, Base, check_db_health
from app.events.publisher import start_producer, stop_producer, is_producer_ready
from app.routers.chat import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await start_producer()
    yield
    await stop_producer()
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    docs_url="/docs" if settings.debug else None,
    lifespan=lifespan,
)
app.include_router(router)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "service": "chat-command"}


@app.get("/health/ready", tags=["health"])
async def readiness():
    db_ok = await check_db_health()
    producer_ok = is_producer_ready()
    if db_ok and producer_ok:
        return {"status": "ready", "db": "ok", "kafka_producer": "ok"}
    return JSONResponse(
        status_code=503,
        content={
            "status": "not_ready",
            "db": "ok" if db_ok else "error",
            "kafka_producer": "ok" if producer_ok else "error",
        },
    )
