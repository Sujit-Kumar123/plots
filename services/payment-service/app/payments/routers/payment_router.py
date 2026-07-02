from fastapi import APIRouter

from app.common.responses import ResponseHandler

router = APIRouter(prefix="/api/payments", tags=["payments"])


@router.get(
    "/status",
    summary="Payment integration status",
    description=(
        "Returns the current configuration state of the Stripe integration. "
        "When `configured` is `false`, all payment endpoints are stubs. "
        "See `app/payments/service.py` to wire up Stripe."
    ),
)
async def payment_status():
    return ResponseHandler.ok(
        "Stripe integration not yet configured. See app/payments/service.py to wire up.",
        data={"configured": False},
    )
