import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import engine, Base, check_db_health
from app.projections.consumer import run_consumer, is_consumer_healthy
from app.routers.plot import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    consumer_task = asyncio.create_task(run_consumer())
    app.state.consumer_task = consumer_task
    yield
    consumer_task.cancel()
    try:
        await asyncio.wait_for(consumer_task, timeout=15.0)
    except (asyncio.CancelledError, asyncio.TimeoutError):
        pass
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    docs_url="/docs" if settings.debug else None,
    lifespan=lifespan,
)
app.include_router(router)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "service": "plot-query"}


@app.get("/health/ready", tags=["health"])
async def readiness():
    db_ok = await check_db_health()
    consumer_ok = is_consumer_healthy()
    if db_ok and consumer_ok:
        return {"status": "ready", "db": "ok", "kafka_consumer": "ok"}
    return JSONResponse(
        status_code=503,
        content={
            "status": "not_ready",
            "db": "ok" if db_ok else "error",
            "kafka_consumer": "ok" if consumer_ok else "error",
        },
    )
