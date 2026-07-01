import logging
import secrets
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlencode

import httpx
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.models.profile_models import Profiles
from app.auth.models.role_models import Roles
from app.auth.models.user_models import User
from app.auth.service.auth_service import AuthService
from app.auth.utils import create_access_token, create_refresh_token, hash_password
from app.common.exceptions import ConflictException, InternalException, UnauthorizedException
from app.config import settings

logger = logging.getLogger(__name__)

_GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
_GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
_GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
_GOOGLE_SCOPES = "openid email profile"


class GoogleAuthService:
    """
    Handles Google OAuth2 flow.

    Requires on User model (add via migration):
        google_id: String(255), nullable, unique
        auth_source: String(20), default "email"
        google_refresh_token: String(512), nullable

    Requires in Settings / .env:
        GOOGLE_CLIENT_ID
        GOOGLE_CLIENT_SECRET
        GOOGLE_OAUTH_REDIRECT_URI
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._auth_svc = AuthService(db)

    async def _flush(self) -> None:
        try:
            await self._flush()
        except IntegrityError as exc:
            logger.error("DB integrity error in Google auth service: %s", exc)
            raise InternalException("Authentication data could not be saved")
        except OperationalError as exc:
            logger.error("DB operational error in Google auth service: %s", exc)
            raise InternalException("A database error occurred, please try again")

    # ── Config helpers ────────────────────────────────────────────────────────

    @property
    def _is_configured(self) -> bool:
        return bool(getattr(settings, "google_client_id", None) and getattr(settings, "google_client_secret", None))

    def _require_configured(self) -> None:
        if not self._is_configured:
            raise UnauthorizedException("Google OAuth is not configured")

    # ── Step 1: build redirect URL ────────────────────────────────────────────

    def generate_auth_url(self, state: str | None = None) -> tuple[str, str]:
        """Return (auth_url, state). Frontend redirects the browser here."""
        self._require_configured()
        state = state or secrets.token_urlsafe(32)
        params = {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_oauth_redirect_uri,
            "scope": _GOOGLE_SCOPES,
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }
        return f"{_GOOGLE_AUTH_URL}?{urlencode(params)}", state

    # ── Step 2: exchange code → tokens ────────────────────────────────────────

    async def _exchange_code(self, code: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.post(
                    _GOOGLE_TOKEN_URL,
                    data={
                        "client_id": settings.google_client_id,
                        "client_secret": settings.google_client_secret,
                        "code": code,
                        "grant_type": "authorization_code",
                        "redirect_uri": settings.google_oauth_redirect_uri,
                    },
                )
                if resp.status_code != 200:
                    logger.error("Google token exchange failed: %s %s", resp.status_code, resp.text)
                    raise UnauthorizedException("Failed to exchange Google code for tokens")
                return resp.json()
            except httpx.TimeoutException:
                logger.error("Google token exchange timeout")
                raise UnauthorizedException("Google request timed out")
            except httpx.RequestError as exc:
                logger.error("Google token exchange connection error: %s", exc)
                raise UnauthorizedException("Could not connect to Google, please try again")

    # ── Step 3: fetch Google user info ────────────────────────────────────────

    async def _get_google_user_info(self, access_token: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.get(
                    _GOOGLE_USER_INFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                if resp.status_code != 200:
                    logger.error("Google user info failed: %s %s", resp.status_code, resp.text)
                    raise UnauthorizedException("Failed to fetch Google user info")
                return resp.json()
            except httpx.TimeoutException:
                logger.error("Google user info timeout")
                raise UnauthorizedException("Google request timed out")
            except httpx.RequestError as exc:
                logger.error("Google user info connection error: %s", exc)
                raise UnauthorizedException("Could not connect to Google, please try again")

    # ── Step 4: find or create user ───────────────────────────────────────────

    async def _get_default_role(self) -> Roles | None:
        result = await self.db.execute(select(Roles).where(Roles.short_name == "member"))
        return result.scalar_one_or_none()

    async def _find_user(self, google_id: str, email: str) -> User | None:
        # Try google_id first
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(
                User.google_id == google_id,  # type: ignore[attr-defined]
                User.is_deleted == False,  # noqa: E712
            )
        )
        user = result.scalar_one_or_none()
        if user:
            return user

        # Fall back to email match
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(
                func.lower(User.email) == email.lower(),
                User.is_deleted == False,  # noqa: E712
            )
        )
        return result.scalar_one_or_none()

    async def _create_or_update_user(
        self,
        google_data: dict[str, Any],
        google_refresh_token: str | None,
    ) -> User:
        google_id = google_data["id"]
        email = google_data["email"]
        fname = google_data.get("given_name", "")
        lname = google_data.get("family_name", "")

        user = await self._find_user(google_id, email)

        if user:
            # Update Google fields on existing user
            user.google_id = google_id  # type: ignore[attr-defined]
            user.is_verified = True
            user.auth_source = "google"  # type: ignore[attr-defined]
            user.last_login = datetime.now(timezone.utc)
            if google_refresh_token:
                user.google_refresh_token = google_refresh_token  # type: ignore[attr-defined]
            await self._flush()

            # Sync profile name if profile exists
            result = await self.db.execute(select(Profiles).where(Profiles.user_id == user.id))
            profile = result.scalar_one_or_none()
            if profile:
                profile.fname = profile.fname or fname
                profile.lname = profile.lname or lname
                await self._flush()

            return user

        # Create new user
        default_role = await self._get_default_role()
        user = User(
            email=email,
            hashed_password=hash_password(secrets.token_urlsafe(32)),
            is_active=True,
            is_verified=True,
            role_id=default_role.id if default_role else None,
            last_login=datetime.now(timezone.utc),
            google_id=google_id,  # type: ignore[call-arg]
            auth_source="google",  # type: ignore[call-arg]
            google_refresh_token=google_refresh_token,  # type: ignore[call-arg]
        )
        self.db.add(user)
        await self.db.flush()

        # Assign in-memory so _build_tokens doesn't trigger a lazy load
        user.role = default_role  # type: ignore[attr-defined]

        self.db.add(Profiles(user_id=user.id, fname=fname, lname=lname))
        await self.db.flush()

        return user

    # ── Step 5: issue app tokens ──────────────────────────────────────────────

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
    ) -> None:
        await self._auth_svc._revoke_active_session(user.id)
        await self._auth_svc._create_session(user, access_token, refresh_token, ip_address, "web")

    # ── Public: full OAuth callback flow ─────────────────────────────────────

    async def authenticate_with_google(
        self,
        code: str,
        ip_address: str | None = None,
    ) -> tuple[User, str, str]:
        """
        Complete OAuth callback.
        Returns (user, access_token, refresh_token) — same shape as AuthService.login_user.
        """
        self._require_configured()

        token_data = await self._exchange_code(code)
        google_user_data = await self._get_google_user_info(token_data["access_token"])

        user = await self._create_or_update_user(
            google_user_data,
            token_data.get("refresh_token"),
        )

        if not user.is_active:
            raise UnauthorizedException("Account is deactivated")

        access_token, refresh_token = self._build_tokens(user)
        await self._create_session(user, access_token, refresh_token, ip_address)

        return user, access_token, refresh_token

    # ── OAuth account management ──────────────────────────────────────────────

    def get_oauth_status(self, user: User) -> dict[str, Any]:
        return {
            "google_linked": bool(getattr(user, "google_id", None)),
            "auth_source": getattr(user, "auth_source", "email"),
            "can_unlink": getattr(user, "auth_source", "email") != "google" or bool(user.hashed_password),
        }

    async def unlink_google_account(self, user: User) -> None:
        if not getattr(user, "google_id", None):
            raise ConflictException("No Google account linked")

        if getattr(user, "auth_source", None) == "google" and not user.hashed_password:
            raise ConflictException("Set a password before unlinking Google so you can still log in")

        user.google_id = None  # type: ignore[attr-defined]
        user.google_refresh_token = None  # type: ignore[attr-defined]
        if getattr(user, "auth_source", None) == "google":
            user.auth_source = "email"  # type: ignore[attr-defined]

        await self.db.flush()
