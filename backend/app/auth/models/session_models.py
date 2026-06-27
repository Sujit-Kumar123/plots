from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.auth.models.user_models import User


class Sessions(Base):
    __tablename__ = "sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Client metadata
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),  # IPv6 max length
        nullable=True,
    )
    geo_location: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    device_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        default="web",
        index=True,
    )

    # Token hashes (never store raw tokens)
    access_token_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    refresh_token_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    # Session lifecycle
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="sessions",
        passive_deletes=True,
        lazy="selectin",
    )

    # Partial unique index: only one active (non-revoked) session per user at a time.
    # When revoked_at IS NULL the row is "active" — PostgreSQL enforces uniqueness
    # only among those rows, so revoked/expired rows are not affected.
    __table_args__ = (
        Index(
            "uq_active_session_per_user",
            "user_id",
            unique=True,
            postgresql_where=text("revoked_at IS NULL"),
        ),
        Index("idx_session_user_expires", "user_id", "expires_at"),
        Index("idx_session_revoked", "revoked_at"),
    )

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def is_expired(self) -> bool:
        return datetime.now(self.expires_at.tzinfo) > self.expires_at

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None

    @property
    def is_valid(self) -> bool:
        return not self.is_expired and not self.is_revoked

    def __repr__(self) -> str:
        return f"<Session user_id={self.user_id} expires_at={self.expires_at}>"
