import uuid

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Sheet(Base):
    __tablename__ = "sheets"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sheet_w: Mapped[float] = mapped_column(Float(), nullable=False)
    sheet_d: Mapped[float] = mapped_column(Float(), nullable=False)
    grid_step: Mapped[float] = mapped_column(Float(), nullable=False)
    elements: Mapped[dict] = mapped_column(
        JSONB(astext_type=Text()), nullable=False, server_default="{}"
    )
