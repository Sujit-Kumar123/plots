"""Furniture catalog model — reference data used to place furniture into plots."""
from sqlalchemy import Float, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class FurnitureCatalogItem(Base):
    __tablename__ = "furniture_catalog"
    __table_args__ = (
        Index("ix_catalog_category", "category"),
        {"schema": "plot_unified"},
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)

    # Real-world dimensions, same units as Plot.sheet_w / grid_step
    width: Mapped[float] = mapped_column(Float, nullable=False)
    height: Mapped[float] = mapped_column(Float, nullable=False)
    depth: Mapped[float] = mapped_column(Float, nullable=False)

    default_color: Mapped[str] = mapped_column(String(9), nullable=False, default="#8b5e3c")
    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
