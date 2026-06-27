from pydantic import BaseModel, Field


class CreateRoleRequest(BaseModel):
    name: str = Field(max_length=255)
    short_name: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=500)


class UpdateRoleRequest(BaseModel):
    name: str | None = Field(None, max_length=255)
    short_name: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=500)


class AssignRoleRequest(BaseModel):
    role_id: str
