import uuid
from datetime import datetime

from pydantic import BaseModel

from app.auth.schemas.response.permission_schemas import PermissionResponse


class RoleResponse(BaseModel):
    id: uuid.UUID
    name: str
    short_name: str | None
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class RolePermissionResponse(BaseModel):
    id: uuid.UUID
    permission: PermissionResponse

    model_config = {"from_attributes": True}


class RoleWithPermissionsResponse(RoleResponse):
    role_permissions: list[RolePermissionResponse]

    model_config = {"from_attributes": True}
