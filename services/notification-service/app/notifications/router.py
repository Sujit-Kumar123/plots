from fastapi import APIRouter, Depends

from app.common.responses import success_response
from app.dependencies import CurrentUser, get_current_user
from app.notifications.schemas import SendEmailRequest, SendSMSRequest
from app.notifications.service import notification_service

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

_ERR = {
    400: {"description": "Bad request"},
    401: {"description": "Missing or invalid auth token"},
    422: {"description": "Validation error"},
}


@router.post(
    "/send-email",
    summary="Send an email notification",
    description=(
        "Sends a transactional email to any address on behalf of the authenticated user. "
        "Uses SendGrid — silently no-ops if `SENDGRID_API_KEY` is unset."
    ),
    responses={**_ERR},
)
async def send_email_endpoint(
    body: SendEmailRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    await notification_service.send_email(body.to, body.subject, body.template_name, body.context)
    return success_response(message="Email sent")


@router.post(
    "/send-sms",
    summary="Send an SMS notification",
    description=(
        "Sends an SMS via Twilio. Silently no-ops if Twilio credentials are not configured."
    ),
    responses={**_ERR},
)
async def send_sms_endpoint(
    body: SendSMSRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    await notification_service.send_sms(body.to_phone, body.message)
    return success_response(message="SMS sent")
