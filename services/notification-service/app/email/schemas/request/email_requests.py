from pydantic import BaseModel, EmailStr


class SendEmailRequest(BaseModel):
    to: EmailStr
    subject: str
    template_name: str
    context: dict = {}


class SendBulkEmailRequest(BaseModel):
    emails: list[SendEmailRequest]
