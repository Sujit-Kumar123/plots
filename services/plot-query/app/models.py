"""Read-side plot models — denormalised for fast listing and search."""
import uuid

from sqlalchemy import Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PlotReadModel(Base):
    __tablename__ = "plots"
    __table_args__ = (
        Index("ix_plot_read_user", "user_id"),
        Index("ix_plot_read_session", "session_id"),
        {"schema": "plot_read"},
    )

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    session_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sheet_w: Mapped[float] = mapped_column(nullable=False)
    sheet_d: Mapped[float] = mapped_column(nullable=False)
    grid_step: Mapped[float] = mapped_column(nullable=False)
    elements: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    version: Mapped[int] = mapped_column(nullable=False, default=1)
    element_count: Mapped[int] = mapped_column(nullable=False, default=0)
