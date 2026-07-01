"""Domain event schemas published to Kafka after successful commands."""
import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel


class PlotCreatedEvent(BaseModel):
    event_type: Literal["plot.created"] = "plot.created"
    plot_id: uuid.UUID
    user_id: uuid.UUID
    session_id: uuid.UUID | None
    name: str
    sheet_w: float
    sheet_d: float
    grid_step: float
    elements: dict[str, Any]
    version: int
    created_at: datetime


class PlotUpdatedEvent(BaseModel):
    event_type: Literal["plot.updated"] = "plot.updated"
    plot_id: uuid.UUID
    user_id: uuid.UUID
    name: str | None
    elements: dict[str, Any] | None
    version: int
    updated_at: datetime


class PlotBulkCreatedEvent(BaseModel):
    event_type: Literal["plot.bulk.created"] = "plot.bulk.created"
    user_id: uuid.UUID
    plot_ids: list[uuid.UUID]
    count: int
    created_at: datetime


class PlotDeletedEvent(BaseModel):
    event_type: Literal["plot.deleted"] = "plot.deleted"
    plot_id: uuid.UUID
    user_id: uuid.UUID
    deleted_at: datetime
