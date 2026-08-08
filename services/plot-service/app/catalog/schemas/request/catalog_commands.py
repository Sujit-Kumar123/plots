"""Command schemas (input contracts for catalog write operations)."""
import uuid

from pydantic import BaseModel, Field


class CreateCatalogItemCommand(BaseModel):
    name: str = Field(..., max_length=255)
    category: str = Field(..., max_length=100)
    width: float
    height: float
    depth: float
    default_color: str = Field(default="#8b5e3c", max_length=9)
    price: float | None = None
    description: str | None = Field(default=None, max_length=500)


class UpdateCatalogItemCommand(BaseModel):
    item_id: uuid.UUID | None = None  # injected from URL path by the router
    name: str | None = Field(default=None, max_length=255)
    category: str | None = Field(default=None, max_length=100)
    width: float | None = None
    height: float | None = None
    depth: float | None = None
    default_color: str | None = Field(default=None, max_length=9)
    price: float | None = None
    description: str | None = Field(default=None, max_length=500)
