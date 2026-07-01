import asyncio
import logging
from pathlib import Path

import httpx
from jinja2 import Environment, FileSystemLoader

from app.config import settings

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).parent / "templates"
_jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=True)

_SENDGRID_URL = "https://api.sendgrid.com/v3/mail/send"
_MAX_RETRIES = 3
_RETRY_DELAYS = [1.0, 2.0, 4.0]


async def send_email(to: str, subject: str, template_name: str, context: dict) -> None:
    if not settings.sendgrid_api_key:
        logger.info("email_skipped to=%s reason=no_sendgrid_key", to)
        return

    template = _jinja_env.get_template(f"{template_name}.html")
    html_content = template.render(**context)

    payload = {
        "personalizations": [{"to": [{"email": to}]}],
        "from": {"email": settings.from_email},
        "subject": subject,
        "content": [{"type": "text/html", "value": html_content}],
    }
    headers = {
        "Authorization": f"Bearer {settings.sendgrid_api_key}",
        "Content-Type": "application/json",
    }

    last_exc: Exception | None = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(_SENDGRID_URL, headers=headers, json=payload)
                resp.raise_for_status()
            logger.info("email_sent to=%s subject=%s", to, subject)
            return
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code < 500:
                raise  # 4xx: bad request or auth — no point retrying
            last_exc = exc
        except Exception as exc:
            last_exc = exc

        logger.warning("email_attempt_failed attempt=%d/%d to=%s error=%s", attempt, _MAX_RETRIES, to, last_exc)
        if attempt < _MAX_RETRIES:
            await asyncio.sleep(_RETRY_DELAYS[attempt - 1])

    raise last_exc  # type: ignore[misc]
