import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator

from app.auth.schemas.response.permission_schemas import PermissionResponse


class RoleResponse(BaseModel):
    id: uuid.UUID
    name: str
    short_name: str
    description: str
    created_at: datetime

    @field_validator("short_name", "description", mode="before")
    @classmethod
    def coerce_none_to_empty(cls, v: str | None) -> str:
        return v or ""

    model_config = {"from_attributes": True}


class RolePermissionResponse(BaseModel):
    id: uuid.UUID
    permission: PermissionResponse

    model_config = {"from_attributes": True}


class RoleWithPermissionsResponse(RoleResponse):
    role_permissions: list[RolePermissionResponse]

    model_config = {"from_attributes": True}
