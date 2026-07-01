from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.auth.models.role_models import Roles
from app.database import Base


class Permissions(Base):
    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    role_permissions: Mapped[List["RolePermissions"]] = relationship(
        "RolePermissions",
        back_populates="permission",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    # Indexes
    __table_args__ = (Index("idx_permissions_name", "name"),)

    def __repr__(self) -> str:
        return f"<Permission code={self.code}>"


class RolePermissions(Base):
    __tablename__ = "role_permissions"

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    role: Mapped["Roles"] = relationship(
        "Roles",
        back_populates="role_permissions",
        passive_deletes=True,
        lazy="selectin",
    )
    permission: Mapped["Permissions"] = relationship(
        "Permissions",
        back_populates="role_permissions",
        passive_deletes=True,
        lazy="selectin",
    )

    # Indexes and constraints
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission_role_id_permission_id"),
        Index("idx_role_permission_role_id", "role_id"),
        Index("idx_role_permission_permission_id", "permission_id"),
    )

    def __repr__(self) -> str:
        return f"<RolePermission role_id={self.role_id} permission_id={self.permission_id}>"
