import logging
import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.models.role_models import Roles
from app.auth.models.user_models import User
from app.common.exceptions import ConflictException, InternalException, NotFoundException

logger = logging.getLogger(__name__)


class RoleService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Helpers ───────────────────────────────────────────────────────────────

    async def _get_role(self, role_id: uuid.UUID) -> Roles:
        result = await self.db.execute(
            select(Roles)
            .options(selectinload(Roles.role_permissions))
            .where(Roles.id == role_id, Roles.is_deleted == False)  # noqa: E712
        )
        role = result.scalar_one_or_none()
        if not role:
            raise NotFoundException("Role not found")
        return role

    async def _flush(self, conflict_msg: str = "Operation failed due to a data conflict") -> None:
        try:
            await self.db.flush()
        except IntegrityError as exc:
            logger.error("DB integrity error in role service: %s", exc)
            raise ConflictException(conflict_msg)
        except OperationalError as exc:
            logger.error("DB operational error in role service: %s", exc)
            raise InternalException("A database error occurred, please try again")

    async def _get_user(self, user_id: uuid.UUID) -> User:
        result = await self.db.execute(
            select(User).where(User.id == user_id, User.is_deleted == False)  # noqa: E712
        )
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundException("User not found")
        return user

    # ── Read ──────────────────────────────────────────────────────────────────

    async def list_roles(self) -> list[Roles]:
        result = await self.db.execute(
            select(Roles)
            .options(selectinload(Roles.role_permissions))
            .where(Roles.is_deleted == False)  # noqa: E712
            .order_by(Roles.name)
        )
        return list(result.scalars().all())

    async def get_role(self, role_id: uuid.UUID) -> Roles:
        return await self._get_role(role_id)

    # ── Create ────────────────────────────────────────────────────────────────

    async def create_role(
        self,
        name: str,
        short_name: str | None = None,
        description: str | None = None,
    ) -> Roles:
        existing = await self.db.execute(select(Roles).where(Roles.name == name))
        if existing.scalar_one_or_none():
            raise ConflictException(f"Role '{name}' already exists")

        role = Roles(name=name, short_name=short_name, description=description)
        self.db.add(role)
        await self._flush(f"Role '{name}' already exists")
        await self.db.refresh(role, attribute_names=["role_permissions"])
        return role

    # ── Update ────────────────────────────────────────────────────────────────

    async def update_role(
        self,
        role_id: uuid.UUID,
        name: str | None = None,
        short_name: str | None = None,
        description: str | None = None,
    ) -> Roles:
        role = await self._get_role(role_id)

        if name is not None and name != role.name:
            clash = await self.db.execute(
                select(Roles).where(Roles.name == name, Roles.id != role_id)
            )
            if clash.scalar_one_or_none():
                raise ConflictException(f"Role '{name}' already exists")
            role.name = name

        if short_name is not None:
            role.short_name = short_name
        if description is not None:
            role.description = description

        await self._flush(f"Role '{name}' already exists")
        return role

    # ── Delete ────────────────────────────────────────────────────────────────

    async def delete_role(self, role_id: uuid.UUID) -> None:
        role = await self._get_role(role_id)

        active_users = await self.db.execute(
            select(User).where(
                User.role_id == role_id,
                User.is_deleted == False,  # noqa: E712
            )
        )
        if active_users.scalars().first():
            raise ConflictException("Cannot delete a role that is assigned to active users")
        # role.is_deleted = True
        await self.db.delete(role)
        await self._flush()

    # ── Assign / Unassign ─────────────────────────────────────────────────────

    async def assign_role(self, user_id: uuid.UUID, role_id: uuid.UUID) -> User:
        user = await self._get_user(user_id)
        await self._get_role(role_id)  # validates role exists

        user.role_id = role_id
        await self._flush()
        await self.db.refresh(user, attribute_names=["role"])
        return user

    async def unassign_role(self, user_id: uuid.UUID) -> User:
        user = await self._get_user(user_id)
        if user.role_id is None:
            raise ConflictException("User has no role assigned")

        user.role_id = None
        await self._flush()
        await self.db.refresh(user, attribute_names=["role"])
        return user
