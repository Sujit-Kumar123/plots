from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.auth.models.permission_models import RolePermissions
    from app.auth.models.user_models import User


class Roles(Base):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    short_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    users: Mapped[List["User"]] = relationship(
        "User",
        back_populates="role",
        lazy="selectin",
    )
    role_permissions: Mapped[List["RolePermissions"]] = relationship(
        "RolePermissions",
        back_populates="role",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    # Indexes
    __table_args__ = (Index("idx_roles_short_name", "short_name"),)

    def __repr__(self) -> str:
        return f"<Role name={self.name}>"
