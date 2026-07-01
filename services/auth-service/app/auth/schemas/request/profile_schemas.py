from pydantic import BaseModel, Field


class UpdateProfileRequest(BaseModel):
    fname: str | None = Field(None, max_length=255)
    lname: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=50)
    company: str | None = Field(None, max_length=255)
    department: str | None = Field(None, max_length=255)
    designation: str | None = Field(None, max_length=255)
    company_role: str | None = Field(None, max_length=255)
    location: str | None = Field(None, max_length=255)
    photo: str | None = None
