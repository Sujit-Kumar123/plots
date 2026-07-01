import logging
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload, selectinload

from app.auth.models.permission_models import RolePermissions
from app.auth.models.profile_models import Profiles
from app.auth.models.role_models import Roles
from app.auth.models.session_models import Sessions
from app.auth.models.token_models import PasswordResetToken
from app.auth.models.user_models import User
from app.auth.utils import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_reset_token,
    hash_password,
    hash_reset_token,
    hash_token,
    verify_password,
)
from app.common.exceptions import (
    ConflictException,
    InternalException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)
from app.config import settings

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Private helpers ───────────────────────────────────────────────────────

    async def _flush(self, conflict_msg: str = "Operation failed due to a data conflict") -> None:
        try:
            await self.db.flush()
        except IntegrityError as exc:
            logger.error("DB integrity error: %s", exc)
            raise ConflictException(conflict_msg)
        except OperationalError as exc:
            logger.error("DB operational error: %s", exc)
            raise InternalException("A database error occurred, please try again")

    async def _get_user_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.email == email, User.is_deleted == False)  # noqa: E712
        )
        return result.scalar_one_or_none()

    async def _get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.db.execute(
            select(User).where(User.id == user_id, User.is_deleted == False)  # noqa: E712
        )
        return result.scalar_one_or_none()

    async def get_user_with_relations(self, user_id: uuid.UUID) -> User | None:
        """Reload user with profile and full role→permissions chain eager-loaded.

        Uses populate_existing=True so the identity-map object (potentially
        expired after a flush) is always refreshed from the DB result.
        noload() prevents circular lazy-loads on back-references.
        """
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
        return result.scalar_one_or_none()

    async def _get_default_role(self) -> Roles | None:
        result = await self.db.execute(select(Roles).where(Roles.short_name == "member"))
        return result.scalar_one_or_none()

    async def _get_active_session(self, user_id: uuid.UUID) -> Sessions | None:
        result = await self.db.execute(
            select(Sessions).where(
                Sessions.user_id == user_id,
                Sessions.revoked_at == None,  # noqa: E711
            )
        )
        return result.scalar_one_or_none()

    async def _revoke_active_session(self, user_id: uuid.UUID) -> None:
        session = await self._get_active_session(user_id)
        if session:
            session.revoked_at = datetime.now(timezone.utc)
            await self._flush()

    def _build_tokens(self, user: User) -> tuple[str, str]:
        role_name = user.role.short_name if user.role else ""
        return (
            create_access_token(str(user.id), role_name),
            create_refresh_token(str(user.id), role_name),
        )

    async def _create_session(
        self,
        user: User,
        access_token: str,
        refresh_token: str,
        ip_address: str | None = None,
        device_type: str = "web",
    ) -> Sessions:
        session = Sessions(
            user_id=user.id,
            access_token_hash=hash_token(access_token),
            refresh_token_hash=hash_token(refresh_token),
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days),
            ip_address=ip_address,
            device_type=device_type,
        )
        self.db.add(session)
        await self._flush()
        return session

    # ── Auth ──────────────────────────────────────────────────────────────────

    async def register_user(
        self,
        email: str,
        password: str,
        fname: str | None = None,
        lname: str | None = None,
        ip_address: str | None = None,
    ) -> tuple[User, str, str]:
        if await self._get_user_by_email(email):
            raise ConflictException("Email already registered")

        default_role = await self._get_default_role()

        user = User(
            email=email,
            hashed_password=hash_password(password),
            role_id=default_role.id if default_role else None,
        )
        self.db.add(user)
        await self._flush("Email already registered")

        self.db.add(Profiles(user_id=user.id, fname=fname, lname=lname))
        await self._flush()

        access_token, refresh_token = self._build_tokens(user)
        await self._create_session(user, access_token, refresh_token, ip_address)

        return user, access_token, refresh_token

    async def login_user(
        self,
        email: str,
        password: str,
        ip_address: str | None = None,
        device_type: str = "web",
    ) -> tuple[User, str, str]:
        user = await self._get_user_by_email(email)

        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedException("Account is deactivated")

        # Enforce one active session — revoke before creating new
        await self._revoke_active_session(user.id)

        user.last_login = datetime.now(timezone.utc)
        await self._flush()

        access_token, refresh_token = self._build_tokens(user)
        await self._create_session(user, access_token, refresh_token, ip_address, device_type)

        return user, access_token, refresh_token

    async def refresh_access_token(self, raw_refresh_token: str) -> tuple[str, str]:
        payload = decode_token(raw_refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid refresh token")

        result = await self.db.execute(
            select(Sessions).where(
                Sessions.refresh_token_hash == hash_token(raw_refresh_token),
                Sessions.revoked_at == None,  # noqa: E711
            )
        )
        session = result.scalar_one_or_none()

        if not session or not session.is_valid:
            raise UnauthorizedException("Session expired or revoked")

        user = await self._get_user_by_id(session.user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or deactivated")

        # Rotate — revoke old session and issue new tokens
        session.revoked_at = datetime.now(timezone.utc)
        await self._flush()

        access_token, refresh_token = self._build_tokens(user)
        await self._create_session(
            user,
            access_token,
            refresh_token,
            session.ip_address,
            session.device_type or "web",
        )

        return access_token, refresh_token

    async def logout_user(self, user_id: uuid.UUID) -> None:
        await self._revoke_active_session(user_id)

    async def get_current_user(self, raw_access_token: str) -> User:
        payload = decode_token(raw_access_token)
        if not payload or payload.get("type") != "access":
            raise UnauthorizedException("Invalid token")

        result = await self.db.execute(
            select(Sessions).where(
                Sessions.access_token_hash == hash_token(raw_access_token),
                Sessions.revoked_at == None,  # noqa: E711
            )
        )
        session = result.scalar_one_or_none()

        if not session or not session.is_valid:
            raise UnauthorizedException("Session expired or revoked")

        user = await self._get_user_by_id(session.user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or deactivated")

        return user

    # ── Password ──────────────────────────────────────────────────────────────

    async def request_password_reset(self, email: str) -> tuple[str, uuid.UUID] | None:
        """Returns (raw_token, user_id) or None if email not found. Caller sends the email."""
        user = await self._get_user_by_email(email)
        if not user:
            return None

        raw_token, hashed_token = generate_reset_token()
        self.db.add(
            PasswordResetToken(
                user_id=user.id,
                token_hash=hashed_token,
                expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            )
        )
        await self._flush()

        return raw_token, user.id

    async def confirm_password_reset(self, raw_token: str, new_password: str) -> None:
        result = await self.db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == hash_reset_token(raw_token),
                PasswordResetToken.is_used == False,  # noqa: E712
                PasswordResetToken.is_deleted == False,  # noqa: E712
            )
        )
        reset = result.scalar_one_or_none()

        if not reset:
            raise ValidationException("Invalid or expired reset token")

        if reset.expires_at < datetime.now(timezone.utc):
            raise ValidationException("Reset token has expired")

        user = await self._get_user_by_id(reset.user_id)
        if not user:
            raise NotFoundException("User not found")

        user.hashed_password = hash_password(new_password)
        reset.is_used = True
        await self._revoke_active_session(user.id)
        await self._flush()

    async def change_password(self, user_id: uuid.UUID, current_password: str, new_password: str) -> None:
        user = await self._get_user_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")

        if not verify_password(current_password, user.hashed_password):
            raise UnauthorizedException("Current password is incorrect")

        user.hashed_password = hash_password(new_password)
        await self._revoke_active_session(user.id)
        await self._flush()
