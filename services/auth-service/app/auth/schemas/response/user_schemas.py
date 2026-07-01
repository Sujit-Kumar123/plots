import uuid
from datetime import datetime

from pydantic import BaseModel

from app.auth.schemas.response.profile_schemas import ProfileResponse
from app.auth.schemas.response.role_schemas import RoleResponse, RoleWithPermissionsResponse


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    is_active: bool
    is_verified: bool
    last_login: datetime | None
    auth_source: str = "email"
    created_at: datetime
    updated_at: datetime
    role: RoleResponse | None

    model_config = {"from_attributes": True}


class UserWithProfileResponse(UserResponse):
    profile: ProfileResponse | None
    role: RoleWithPermissionsResponse | None  # includes permissions

    model_config = {"from_attributes": True}
