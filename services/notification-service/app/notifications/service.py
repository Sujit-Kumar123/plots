import logging

from app.email.service import send_email as _send_email
from app.notifications.sms import send_sms as _send_sms

logger = logging.getLogger(__name__)


class NotificationService:
    async def send_email(self, to: str, subject: str, template_name: str, context: dict) -> None:
        await _send_email(to, subject, template_name, context)

    async def send_sms(self, to_phone: str, message: str) -> None:
        await _send_sms(to_phone, message)

    async def notify(self, email: str, phone: str | None, channel: str, template: str, context: dict) -> None:
        if channel == "email":
            subject = context.pop("subject", "Notification")
            await self.send_email(email, subject, template, context)
        elif channel == "sms" and phone:
            await self.send_sms(phone, context.get("message", ""))


notification_service = NotificationService()
