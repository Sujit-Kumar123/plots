import uuid
from datetime import datetime

from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    file_name: str
    content_type: str
    size_bytes: int
    created_at: datetime
    url: str | None = None

    model_config = {"from_attributes": True}
