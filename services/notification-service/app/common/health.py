from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def liveness():
    return {"status": "ok", "service": "notification-service"}


@router.get("/health/ready")
async def readiness():
    return {"status": "ready"}
