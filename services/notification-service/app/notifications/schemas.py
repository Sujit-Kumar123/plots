from pydantic import BaseModel, EmailStr


class SendEmailRequest(BaseModel):
    to: EmailStr
    subject: str
    template_name: str
    context: dict = {}


class SendSMSRequest(BaseModel):
    to_phone: str
    message: str
