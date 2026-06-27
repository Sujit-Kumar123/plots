from pydantic_settings import BaseSettings


class EmailConfig(BaseSettings):
    # SendGrid
    sendgrid_api_key: str = ""
    from_email: str = "noreply@example.com"

    # Twilio SMS
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""
