import uuid
from datetime import datetime

from pydantic import BaseModel


class ProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    fname: str | None
    lname: str | None
    phone: str | None
    company: str | None
    department: str | None
    designation: str | None
    company_role: str | None
    location: str | None
    photo: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
