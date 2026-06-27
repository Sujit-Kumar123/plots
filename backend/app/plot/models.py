import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.auth.models.user_models import User


class Sheet(Base):
    __tablename__ = "sheets"

    name: Mapped[str] = mapped_column(String(255), nullable=False, default="Untitled Sheet")
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sheet_w: Mapped[float] = mapped_column(nullable=False, default=20.0)
    sheet_d: Mapped[float] = mapped_column(nullable=False, default=20.0)
    grid_step: Mapped[float] = mapped_column(nullable=False, default=1.0)
    # Serialised scene: { blocks, penLines, walls, divPanels, textSprites }
    elements: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    user: Mapped["User"] = relationship("User", lazy="selectin")
