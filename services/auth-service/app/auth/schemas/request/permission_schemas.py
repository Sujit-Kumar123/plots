from pydantic import BaseModel, Field


class CreatePermissionRequest(BaseModel):
    name: str = Field(max_length=255)
    code: str = Field(max_length=255)
    description: str | None = Field(None, max_length=500)


class UpdatePermissionRequest(BaseModel):
    name: str | None = Field(None, max_length=255)
    code: str | None = Field(None, max_length=255)
    description: str | None = Field(None, max_length=500)


class AssignPermissionRequest(BaseModel):
    permission_id: str
