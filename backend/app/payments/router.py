from fastapi import APIRouter

from app.common.responses import success_response

router = APIRouter(prefix="/api/payments", tags=["payments"])


@router.get("/status")
async def payment_status():
    return success_response(
        data={"configured": False},
        message="Stripe integration not yet configured. See app/payments/service.py to wire up.",
    )
