"""Pydantic response schemas for OpenAPI / Swagger documentation."""
from typing import Any

from pydantic import BaseModel


class PlotCommandResponse(BaseModel):
    id: str
    name: str
    version: int


class BulkPlotsAcceptedResponse(BaseModel):
    accepted: int
    ids: list[str]


class PlotItem(BaseModel):
    id: str
    user_id: str
    session_id: str | None
    name: str
    sheet_w: float
    sheet_d: float
    grid_step: float
    elements: dict[str, Any]
    version: int
    element_count: int
    created_at: str
    updated_at: str


class PlotListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[PlotItem]
