import asyncio

from fastapi import APIRouter, Depends, HTTPException, status

from app.common.internal_auth import require_internal_auth
from app.common.responses import success_response
from app.email.schemas import SendBulkEmailRequest, SendEmailRequest
from app.email.service import send_email

router = APIRouter(
    prefix="/api/email",
    tags=["email"],
    dependencies=[Depends(require_internal_auth)],
)

_ERR = {
    400: {"description": "Bad request"},
    403: {"description": "Invalid x-internal-secret header"},
    502: {"description": "Email delivery failed (SendGrid error)"},
}


@router.post(
    "/send",
    status_code=status.HTTP_200_OK,
    summary="Send a single transactional email",
    description=(
        "Renders a Jinja2 template from `email/templates/` and sends it via SendGrid. "
        "Requires the `x-internal-secret` header — this endpoint is called by backend services, "
        "not the browser. If `SENDGRID_API_KEY` is unset the email is silently skipped (dev mode)."
    ),
    responses={**_ERR},
)
async def send_single(body: SendEmailRequest):
    try:
        await send_email(body.to, body.subject, body.template_name, body.context)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Email delivery failed: {exc}",
        )
    return success_response(message="Email sent")


@router.post(
    "/send-bulk",
    status_code=status.HTTP_200_OK,
    summary="Send multiple transactional emails",
    description=(
        "Sends up to N emails concurrently via `asyncio.gather`. "
        "Returns counts of sent vs failed. Partial failures do not raise an error."
    ),
    responses={**_ERR},
)
async def send_bulk(body: SendBulkEmailRequest):
    results = await asyncio.gather(
        *[send_email(r.to, r.subject, r.template_name, r.context) for r in body.emails],
        return_exceptions=True,
    )
    sent = sum(1 for r in results if not isinstance(r, Exception))
    errors = [str(results[i]) for i, r in enumerate(results) if isinstance(r, Exception)]
    return success_response(data={"sent": sent, "failed": len(errors), "errors": errors})
