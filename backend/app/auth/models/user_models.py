from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.auth.models.profile_models import Profiles
    from app.auth.models.role_models import Roles
    from app.auth.models.session_models import Sessions


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # OAuth source tracking
    auth_source: Mapped[str] = mapped_column(String(20), default="email", server_default="email", nullable=False)

    # Google OAuth
    google_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True, index=True)
    google_refresh_token: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # Azure OAuth
    azure_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True, index=True)
    azure_refresh_token: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # One user → one role (direct FK, nullable until assigned)
    role_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relationships
    role: Mapped[Optional["Roles"]] = relationship(
        "Roles",
        back_populates="users",
        lazy="selectin",
    )
    profile: Mapped[Optional["Profiles"]] = relationship(
        "Profiles",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
    sessions: Mapped[List["Sessions"]] = relationship(
        "Sessions",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<User email={self.email}>"
