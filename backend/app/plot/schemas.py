import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SheetCreate(BaseModel):
    name: str = Field(default="Untitled Sheet", max_length=255)
    sheet_w: float = Field(default=20.0, gt=0)
    sheet_d: float = Field(default=20.0, gt=0)
    grid_step: float = Field(default=1.0, gt=0)
    elements: dict[str, Any] = Field(default_factory=dict)


class SheetUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    sheet_w: float | None = Field(default=None, gt=0)
    sheet_d: float | None = Field(default=None, gt=0)
    grid_step: float | None = Field(default=None, gt=0)
    elements: dict[str, Any] | None = None


class SheetResponse(BaseModel):
    id: uuid.UUID
    name: str
    sheet_w: float
    sheet_d: float
    grid_step: float
    elements: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SheetListItem(BaseModel):
    id: uuid.UUID
    name: str
    sheet_w: float
    sheet_d: float
    updated_at: datetime

    model_config = {"from_attributes": True}
