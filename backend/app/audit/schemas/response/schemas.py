import uuid
from datetime import datetime

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID | None
    action: str
    resource_type: str
    resource_id: uuid.UUID | None
    details: dict | None
    ip_address: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
