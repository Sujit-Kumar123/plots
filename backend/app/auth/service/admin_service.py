import logging
import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.models import Roles, User
from app.common.exceptions import ForbiddenException, InternalException, NotFoundException
from app.common.pagination import PaginationParams

logger = logging.getLogger(__name__)


async def _flush(db: AsyncSession) -> None:
    try:
        await db.flush()
    except IntegrityError as exc:
        logger.error("DB integrity error in admin service: %s", exc)
        raise InternalException("Operation failed due to a data conflict")
    except OperationalError as exc:
        logger.error("DB operational error in admin service: %s", exc)
        raise InternalException("A database error occurred, please try again")


async def list_users(
    db: AsyncSession,
    pagination: PaginationParams,
    role: str | None = None,
    is_active: bool | None = None,
) -> tuple[list[User], int]:
    query = select(User).options(selectinload(User.profile)).where(User.is_deleted == False)

    if role:
        query = query.join(User.role).where(Roles.short_name == role)
    if is_active is not None:
        query = query.where(User.is_active == is_active)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    query = query.offset(pagination.offset).limit(pagination.page_size).order_by(User.created_at.desc())
    result = await db.execute(query)
    users = list(result.scalars().all())

    return users, total


async def get_user_detail(db: AsyncSession, user_id: uuid.UUID) -> User:
    result = await db.execute(
        select(User).options(selectinload(User.profile)).where(User.id == user_id, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundException("User not found")
    return user


async def update_user(
    db: AsyncSession, user_id: uuid.UUID, current_user: User, role_id: uuid.UUID | None = None, is_active: bool | None = None
) -> User:
    user = await get_user_detail(db, user_id)

    if role_id is not None:
        role_result = await db.execute(select(Roles).where(Roles.id == role_id))
        role_obj = role_result.scalar_one_or_none()
        if not role_obj:
            raise NotFoundException(f"Role not found")
        if role_obj.short_name == "superadmin" and (not current_user.role or current_user.role.short_name != "superadmin"):
            raise ForbiddenException("Only superadmins can assign superadmin role")
        user.role_id = role_obj.id

    if is_active is not None:
        user.is_active = is_active

    await _flush(db)

    # Re-query after flush: SQLAlchemy expires all attributes on flush, so
    # accessing them later triggers an implicit lazy-load which is forbidden
    # in async mode (MissingGreenlet). Eager-load everything the response needs.
    result = await db.execute(
        select(User)
        .options(selectinload(User.role), selectinload(User.profile))
        .where(User.id == user_id)
    )
    # Use scalar_one_or_none to avoid NoResultFound on a race-condition delete
    updated = result.scalar_one_or_none()
    if not updated:
        raise NotFoundException("User not found after update")
    return updated


async def soft_delete_user(db: AsyncSession, user_id: uuid.UUID, current_user: User) -> None:
    if user_id == current_user.id:
        raise ForbiddenException("Cannot delete yourself")
    user = await get_user_detail(db, user_id)
    user.is_deleted = True
    user.is_active = False
    await _flush(db)


async def deactivate_user(db: AsyncSession, user_id: uuid.UUID, current_user: User) -> User:
    if user_id == current_user.id:
        raise ForbiddenException("Cannot deactivate yourself")
    user = await get_user_detail(db, user_id)
    user.is_active = False
    await _flush(db)
    return user


async def activate_user(db: AsyncSession, user_id: uuid.UUID) -> User:
    user = await get_user_detail(db, user_id)
    user.is_active = True
    await _flush(db)
    return user
