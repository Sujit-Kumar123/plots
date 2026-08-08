"""Pydantic response schemas for OpenAPI / Swagger documentation."""
from pydantic import BaseModel


class CatalogItem(BaseModel):
    id: str
    name: str
    category: str
    width: float
    height: float
    depth: float
    default_color: str
    price: float | None
    description: str | None
    created_at: str
    updated_at: str


class CatalogListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[CatalogItem]
