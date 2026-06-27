import uuid
from datetime import datetime

from pydantic import BaseModel


class PermissionResponse(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
