from fastapi import HTTPException


async def create_checkout_session(**kwargs):
    raise HTTPException(status_code=501, detail="Stripe checkout is not yet configured")


async def handle_webhook(payload: bytes, signature: str):
    raise HTTPException(status_code=501, detail="Stripe webhook is not yet configured")


async def create_customer(email: str, name: str | None = None):
    raise HTTPException(status_code=501, detail="Stripe customer creation is not yet configured")
