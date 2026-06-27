from typing import Literal

from app.notifications.email import send_email as _send_email
from app.notifications.sms import send_sms as _send_sms


class NotificationService:
    async def send_email(self, to: str, subject: str, template_name: str, context: dict) -> None:
        await _send_email(to, subject, template_name, context)

    async def send_sms(self, to_phone: str, message: str) -> None:
        await _send_sms(to_phone, message)

    async def notify(self, user, channel: Literal["email", "sms"], template: str, context: dict) -> None:
        """Send notification to a user. `user` should have `email` and optionally `profile.phone`."""
        if channel == "email":
            subject = context.pop("subject", "Notification")
            await self.send_email(user.email, subject, template, context)
        elif channel == "sms":
            phone = getattr(user, "phone", None) or (user.profile.phone if hasattr(user, "profile") else None)
            if phone:
                message = context.get("message", "")
                await self.send_sms(phone, message)


notification_service = NotificationService()
