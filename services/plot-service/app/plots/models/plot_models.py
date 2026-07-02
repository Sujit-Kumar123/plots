"""Unified plot model for both write and read operations (plot_unified schema)."""
import uuid

from sqlalchemy import Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Plot(Base):
    __tablename__ = "plots"
    __table_args__ = (
        Index("ix_plot_user", "user_id"),
        Index("ix_plot_session", "session_id"),
        {"schema": "plot_unified"},
    )

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    session_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, default="Untitled Plot")

    # Sheet geometry
    sheet_w: Mapped[float] = mapped_column(nullable=False, default=20.0)
    sheet_d: Mapped[float] = mapped_column(nullable=False, default=20.0)
    grid_step: Mapped[float] = mapped_column(nullable=False, default=1.0)

    # Full scene: { blocks, penLines, walls, divPanels, textSprites }
    elements: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Optimistic locking version
    version: Mapped[int] = mapped_column(nullable=False, default=1)

    # Denormalized count for fast listing
    element_count: Mapped[int] = mapped_column(nullable=False, default=0)
