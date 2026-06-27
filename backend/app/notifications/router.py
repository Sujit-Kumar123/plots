from fastapi import APIRouter, Depends

from app.auth.dependencies import require_permission
from app.auth.models import User
from app.common.responses import success_response
from app.notifications.schemas import SendEmailRequest, SendSMSRequest
from app.notifications.service import notification_service

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.post("/send-email")
async def send_email_endpoint(
    body: SendEmailRequest,
    current_user: User = Depends(require_permission("notifications:write")),
):
    await notification_service.send_email(body.to, body.subject, body.template_name, body.context)
    return success_response(message="Email sent")


@router.post("/send-sms")
async def send_sms_endpoint(
    body: SendSMSRequest,
    current_user: User = Depends(require_permission("notifications:write")),
):
    await notification_service.send_sms(body.to_phone, body.message)
    return success_response(message="SMS sent")
