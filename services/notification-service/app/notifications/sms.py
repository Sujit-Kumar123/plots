import base64

import httpx

from app.config import settings


async def send_sms(to_phone: str, message: str) -> None:
    if not settings.twilio_account_sid or not settings.twilio_auth_token:
        import structlog

        logger = structlog.get_logger()
        await logger.ainfo("sms_skipped", to=to_phone, reason="no Twilio credentials")
        return

    url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.twilio_account_sid}/Messages.json"
    auth = base64.b64encode(f"{settings.twilio_account_sid}:{settings.twilio_auth_token}".encode()).decode()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            headers={"Authorization": f"Basic {auth}"},
            data={
                "From": settings.twilio_from_number,
                "To": to_phone,
                "Body": message,
            },
        )
        response.raise_for_status()
