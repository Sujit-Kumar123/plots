import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator


class PermissionResponse(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    description: str
    created_at: datetime

    @field_validator("description", mode="before")
    @classmethod
    def coerce_none_to_empty(cls, v: str | None) -> str:
        return v or ""

    model_config = {"from_attributes": True}
