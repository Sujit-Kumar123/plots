from pydantic import BaseModel


class PaymentPlaceholder(BaseModel):
    message: str = "Stripe integration not yet configured"
