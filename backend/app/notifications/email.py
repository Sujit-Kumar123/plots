from pathlib import Path

import httpx
from jinja2 import Environment, FileSystemLoader

from app.config import settings

TEMPLATE_DIR = Path(__file__).parent / "templates"
jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=True)


async def send_email(to: str, subject: str, template_name: str, context: dict) -> None:
    if not settings.sendgrid_api_key:
        import structlog

        logger = structlog.get_logger()
        await logger.ainfo("email_skipped", to=to, subject=subject, reason="no SendGrid API key")
        return

    template = jinja_env.get_template(f"{template_name}.html")
    html_content = template.render(**context)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={
                "Authorization": f"Bearer {settings.sendgrid_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "personalizations": [{"to": [{"email": to}]}],
                "from": {"email": settings.from_email},
                "subject": subject,
                "content": [{"type": "text/html", "value": html_content}],
            },
        )
        response.raise_for_status()
