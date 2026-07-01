import uuid
from datetime import datetime

from pydantic import BaseModel


class PasswordResetTokenResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    expires_at: datetime
    is_used: bool
    created_at: datetime

    model_config = {"from_attributes": True}
