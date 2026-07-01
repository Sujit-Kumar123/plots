from fastapi import APIRouter

from app.common.responses import success_response

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
    return success_response(
        data={"configured": False},
        message="Stripe integration not yet configured. See app/payments/service.py to wire up.",
    )
