from app.worker.celery_app import celery_app


@celery_app.task(name="send_email_task")
def send_email_task(to: str, subject: str, template_name: str, context: dict) -> dict:
    """
    Sample Celery task demonstrating the pattern.
    Celery tasks are sync by default; use sync httpx here.
    """
    from pathlib import Path

    import httpx
    from jinja2 import Environment, FileSystemLoader

    from app.config import settings

    if not settings.sendgrid_api_key:
        return {"status": "skipped", "reason": "no SendGrid API key"}

    template_dir = Path(__file__).parent.parent / "notifications" / "templates"
    jinja_env = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=True)
    template = jinja_env.get_template(f"{template_name}.html")
    html_content = template.render(**context)

    response = httpx.post(
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
    return {"status": "sent", "to": to}
