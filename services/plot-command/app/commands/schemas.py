import uuid
from typing import Any

from pydantic import BaseModel, Field


class CreatePlotCommand(BaseModel):
    name: str = Field(default="Untitled Plot", max_length=255)
    session_id: uuid.UUID | None = None
    sheet_w: float = 20.0
    sheet_d: float = 20.0
    grid_step: float = 1.0
    elements: dict[str, Any] = Field(default_factory=dict)


class UpdatePlotCommand(BaseModel):
    plot_id: uuid.UUID
    name: str | None = Field(default=None, max_length=255)
    sheet_w: float | None = None
    sheet_d: float | None = None
    grid_step: float | None = None
    elements: dict[str, Any] | None = None


class BulkCreatePlotsCommand(BaseModel):
    plots: list[CreatePlotCommand] = Field(..., min_length=1, max_length=500)


class DeletePlotCommand(BaseModel):
    plot_id: uuid.UUID
