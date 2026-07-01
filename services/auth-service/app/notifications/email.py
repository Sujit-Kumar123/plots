import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


async def send_email(to: str, subject: str, template_name: str, context: dict) -> None:
    """Delegate email delivery to email-service."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{settings.email_service_url}/api/email/send",
                json={"to": to, "subject": subject, "template_name": template_name, "context": context},
            )
            resp.raise_for_status()
    except Exception as exc:
        logger.error("email_service_error to=%s subject=%s: %s", to, subject, exc)
        raise
