import logging
import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload, selectinload

from app.auth.models.permission_models import RolePermissions
from app.auth.models.profile_models import Profiles
from app.auth.models.role_models import Roles
from app.auth.models.user_models import User
from app.auth.utils import hash_password, verify_password
from app.common.exceptions import InternalException, NotFoundException, UnauthorizedException

logger = logging.getLogger(__name__)


class ProfileService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _flush(self) -> None:
        try:
            await self.db.flush()
        except IntegrityError as exc:
            logger.error("DB integrity error in profile service: %s", exc)
            raise InternalException("Profile update failed due to a data conflict")
        except OperationalError as exc:
            logger.error("DB operational error in profile service: %s", exc)
            raise InternalException("A database error occurred, please try again")

    async def get_user_with_profile(self, user_id: uuid.UUID) -> User:
        result = await self.db.execute(
            select(User)
            .options(
                noload(User.sessions),
                selectinload(User.profile),
                selectinload(User.role).options(
                    noload(Roles.users),
                    selectinload(Roles.role_permissions).options(
                        noload(RolePermissions.role),
                        selectinload(RolePermissions.permission),
                    ),
                ),
            )
            .where(User.id == user_id, User.is_deleted == False)  # noqa: E712
            .execution_options(populate_existing=True)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundException("User not found")
        return user

    async def update_profile(
        self,
        user_id: uuid.UUID,
        fname: str | None = None,
        lname: str | None = None,
        phone: str | None = None,
        company: str | None = None,
        department: str | None = None,
        designation: str | None = None,
        company_role: str | None = None,
        location: str | None = None,
        photo: str | None = None,
    ) -> Profiles:
        result = await self.db.execute(select(Profiles).where(Profiles.user_id == user_id))
        profile = result.scalar_one_or_none()
        if not profile:
            profile = Profiles(user_id=user_id)
            self.db.add(profile)

        if fname is not None:
            profile.fname = fname
        if lname is not None:
            profile.lname = lname
        if phone is not None:
            profile.phone = phone
        if company is not None:
            profile.company = company
        if department is not None:
            profile.department = department
        if designation is not None:
            profile.designation = designation
        if company_role is not None:
            profile.company_role = company_role
        if location is not None:
            profile.location = location
        if photo is not None:
            profile.photo = photo

        await self._flush()
        return profile

    async def change_password(self, user_id: uuid.UUID, current_password: str, new_password: str) -> None:
        result = await self.db.execute(
            select(User).where(User.id == user_id, User.is_deleted == False)  # noqa: E712
        )
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundException("User not found")

        if not verify_password(current_password, user.hashed_password):
            raise UnauthorizedException("Current password is incorrect")

        user.hashed_password = hash_password(new_password)
        await self._flush()
