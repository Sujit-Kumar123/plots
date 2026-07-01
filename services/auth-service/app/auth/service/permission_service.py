import logging
import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models.permission_models import Permissions, RolePermissions
from app.auth.models.role_models import Roles
from app.common.exceptions import ConflictException, InternalException, NotFoundException
from app.common.pagination import PaginationParams
from app.common.permissions.codes import PERMISSIONS

logger = logging.getLogger(__name__)


class PermissionService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Helpers ───────────────────────────────────────────────────────────────

    async def _flush(self, conflict_msg: str = "Operation failed due to a data conflict") -> None:
        try:
            await self.db.flush()
        except IntegrityError as exc:
            logger.error("DB integrity error in permission service: %s", exc)
            raise ConflictException(conflict_msg)
        except OperationalError as exc:
            logger.error("DB operational error in permission service: %s", exc)
            raise InternalException("A database error occurred, please try again")

    async def _get_permission(self, permission_id: uuid.UUID) -> Permissions:
        result = await self.db.execute(
            select(Permissions).where(
                Permissions.id == permission_id,
                Permissions.is_deleted == False,  # noqa: E712
            )
        )
        perm = result.scalar_one_or_none()
        if not perm:
            raise NotFoundException("Permission not found")
        return perm

    async def _get_role(self, role_id: uuid.UUID) -> Roles:
        result = await self.db.execute(
            select(Roles).where(
                Roles.id == role_id,
                Roles.is_deleted == False,  # noqa: E712
            )
        )
        role = result.scalar_one_or_none()
        if not role:
            raise NotFoundException("Role not found")
        return role

    # ── Read ──────────────────────────────────────────────────────────────────

    async def list_permissions(self, pagination: PaginationParams) -> tuple[list[Permissions], int]:
        base = select(Permissions).where(Permissions.is_deleted == False)  # noqa: E712
        total = (await self.db.execute(select(func.count()).select_from(base.subquery()))).scalar_one()
        result = await self.db.execute(
            base.order_by(Permissions.name).offset(pagination.offset).limit(pagination.page_size)
        )
        return list(result.scalars().all()), total

    async def get_permission(self, permission_id: uuid.UUID) -> Permissions:
        return await self._get_permission(permission_id)

    async def list_missing_permission_codes(self) -> list[str]:
        result = await self.db.execute(
            select(Permissions.code).where(Permissions.is_deleted == False)  # noqa: E712
        )
        existing = set(result.scalars().all())
        return [code for code in PERMISSIONS if code not in existing]

    # ── Create ────────────────────────────────────────────────────────────────

    async def create_permission(
        self,
        name: str,
        code: str,
        description: str | None = None,
    ) -> Permissions:
        existing = await self.db.execute(select(Permissions).where(Permissions.code == code))
        if existing.scalar_one_or_none():
            raise ConflictException(f"Permission with code '{code}' already exists")

        perm = Permissions(name=name, code=code, description=description)
        self.db.add(perm)
        await self._flush(f"Permission with code '{code}' already exists")
        await self.db.refresh(perm)
        return perm

    # ── Update ────────────────────────────────────────────────────────────────

    async def update_permission(
        self,
        permission_id: uuid.UUID,
        name: str | None = None,
        code: str | None = None,
        description: str | None = None,
    ) -> Permissions:
        perm = await self._get_permission(permission_id)

        if code is not None and code != perm.code:
            clash = await self.db.execute(
                select(Permissions).where(
                    Permissions.code == code,
                    Permissions.id != permission_id,
                )
            )
            if clash.scalar_one_or_none():
                raise ConflictException(f"Permission with code '{code}' already exists")
            perm.code = code

        if name is not None:
            perm.name = name
        if description is not None:
            perm.description = description

        await self._flush(f"Permission with code '{code}' already exists")
        return perm

    # ── Delete ────────────────────────────────────────────────────────────────

    async def delete_permission(self, permission_id: uuid.UUID) -> None:
        perm = await self._get_permission(permission_id)

        assigned = await self.db.execute(select(RolePermissions).where(RolePermissions.permission_id == permission_id))
        if assigned.scalars().first():
            raise ConflictException("Cannot delete a permission that is assigned to one or more roles")

        perm.is_deleted = True
        await self._flush()

    # ── Assign / Unassign to Role ─────────────────────────────────────────────

    async def assign_to_role(self, role_id: uuid.UUID, permission_id: uuid.UUID) -> Roles:
        await self._get_permission(permission_id)
        role = await self._get_role(role_id)

        existing = await self.db.execute(
            select(RolePermissions).where(
                RolePermissions.role_id == role_id,
                RolePermissions.permission_id == permission_id,
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictException("Permission already assigned to this role")

        self.db.add(RolePermissions(role_id=role_id, permission_id=permission_id))
        await self._flush("Permission already assigned to this role")
        await self.db.refresh(role, attribute_names=["role_permissions"])
        return role

    async def unassign_from_role(self, role_id: uuid.UUID, permission_id: uuid.UUID) -> Roles:
        await self._get_permission(permission_id)
        role = await self._get_role(role_id)

        result = await self.db.execute(
            select(RolePermissions).where(
                RolePermissions.role_id == role_id,
                RolePermissions.permission_id == permission_id,
            )
        )
        rp = result.scalar_one_or_none()
        if not rp:
            raise NotFoundException("Permission is not assigned to this role")

        await self.db.delete(rp)
        await self._flush()
        await self.db.refresh(role, attribute_names=["role_permissions"])
        return role
