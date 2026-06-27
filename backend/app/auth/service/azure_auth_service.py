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

_AZURE_AUTH_URL = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize"
_AZURE_TOKEN_URL = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
_AZURE_USER_INFO_URL = "https://graph.microsoft.com/v1.0/me"
_AZURE_SCOPES = "openid email profile User.Read"


class AzureAuthService:
    """
    Handles Azure AD OAuth2 flow (single-tenant or multi-tenant).

    Requires on User model (add via migration):
        azure_id: String(255), nullable, unique
        auth_source: String(20), default "email"   ← shared with Google
        azure_refresh_token: String(512), nullable

    Requires in Settings / .env:
        AZURE_CLIENT_ID
        AZURE_CLIENT_SECRET
        AZURE_TENANT_ID          (use "common" for multi-tenant)
        AZURE_OAUTH_REDIRECT_URI
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._auth_svc = AuthService(db)

    async def _flush(self) -> None:
        try:
            await self._flush()
        except IntegrityError as exc:
            logger.error("DB integrity error in Azure auth service: %s", exc)
            raise InternalException("Authentication data could not be saved")
        except OperationalError as exc:
            logger.error("DB operational error in Azure auth service: %s", exc)
            raise InternalException("A database error occurred, please try again")

    # ── Config helpers ────────────────────────────────────────────────────────

    @property
    def _tenant(self) -> str:
        return getattr(settings, "azure_tenant_id", "common")

    @property
    def _is_configured(self) -> bool:
        return bool(getattr(settings, "azure_client_id", None) and getattr(settings, "azure_client_secret", None))

    def _require_configured(self) -> None:
        if not self._is_configured:
            raise UnauthorizedException("Azure OAuth is not configured")

    def _auth_url(self) -> str:
        return _AZURE_AUTH_URL.format(tenant=self._tenant)

    def _token_url(self) -> str:
        return _AZURE_TOKEN_URL.format(tenant=self._tenant)

    # ── Step 1: build redirect URL ────────────────────────────────────────────

    def generate_auth_url(self, state: str | None = None) -> tuple[str, str]:
        """Return (auth_url, state). Frontend redirects the browser here."""
        self._require_configured()
        state = state or secrets.token_urlsafe(32)
        params = {
            "client_id": settings.azure_client_id,
            "redirect_uri": settings.azure_oauth_redirect_uri,
            "scope": _AZURE_SCOPES,
            "response_type": "code",
            "response_mode": "query",
            "state": state,
        }
        return f"{self._auth_url()}?{urlencode(params)}", state

    # ── Step 2: exchange code → tokens ────────────────────────────────────────

    async def _exchange_code(self, code: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.post(
                    self._token_url(),
                    data={
                        "client_id": settings.azure_client_id,
                        "client_secret": settings.azure_client_secret,
                        "code": code,
                        "grant_type": "authorization_code",
                        "redirect_uri": settings.azure_oauth_redirect_uri,
                        "scope": _AZURE_SCOPES,
                    },
                )
                if resp.status_code != 200:
                    logger.error("Azure token exchange failed: %s %s", resp.status_code, resp.text)
                    raise UnauthorizedException("Failed to exchange Azure code for tokens")
                return resp.json()
            except httpx.TimeoutException:
                logger.error("Azure token exchange timeout")
                raise UnauthorizedException("Azure request timed out")
            except httpx.RequestError as exc:
                logger.error("Azure token exchange connection error: %s", exc)
                raise UnauthorizedException("Could not connect to Azure, please try again")

    # ── Step 3: fetch Azure user info via Microsoft Graph ─────────────────────

    async def _get_azure_user_info(self, access_token: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.get(
                    _AZURE_USER_INFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                if resp.status_code != 200:
                    logger.error("Azure user info failed: %s %s", resp.status_code, resp.text)
                    raise UnauthorizedException("Failed to fetch Azure user info")
                return resp.json()
            except httpx.TimeoutException:
                logger.error("Azure user info timeout")
                raise UnauthorizedException("Azure request timed out")
            except httpx.RequestError as exc:
                logger.error("Azure user info connection error: %s", exc)
                raise UnauthorizedException("Could not connect to Azure, please try again")

    # ── Step 4: find or create user ───────────────────────────────────────────

    async def _get_default_role(self) -> Roles | None:
        result = await self.db.execute(select(Roles).where(Roles.short_name == "member"))
        return result.scalar_one_or_none()

    async def _find_user(self, azure_id: str, email: str) -> User | None:
        # Try azure_id first
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.role))
            .where(
                User.azure_id == azure_id,  # type: ignore[attr-defined]
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

    def _extract_user_data(self, azure_data: dict[str, Any]) -> dict[str, str]:
        """Normalise Microsoft Graph /me response into flat fields."""
        # Microsoft Graph returns: id, displayName, givenName, surname, mail, userPrincipalName
        email = azure_data.get("mail") or azure_data.get("userPrincipalName", "")
        return {
            "azure_id": azure_data["id"],
            "email": email,
            "fname": azure_data.get("givenName", ""),
            "lname": azure_data.get("surname", ""),
        }

    async def _create_or_update_user(
        self,
        azure_data: dict[str, Any],
        azure_refresh_token: str | None,
    ) -> User:
        data = self._extract_user_data(azure_data)
        azure_id = data["azure_id"]
        email = data["email"]

        if not email:
            raise UnauthorizedException("Azure account has no accessible email address")

        user = await self._find_user(azure_id, email)

        if user:
            user.azure_id = azure_id  # type: ignore[attr-defined]
            user.is_verified = True
            user.auth_source = "azure"  # type: ignore[attr-defined]
            user.last_login = datetime.now(timezone.utc)
            if azure_refresh_token:
                user.azure_refresh_token = azure_refresh_token  # type: ignore[attr-defined]
            await self._flush()

            # Sync profile name if not already set
            result = await self.db.execute(select(Profiles).where(Profiles.user_id == user.id))
            profile = result.scalar_one_or_none()
            if profile:
                profile.fname = profile.fname or data["fname"]
                profile.lname = profile.lname or data["lname"]
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
            azure_id=azure_id,  # type: ignore[call-arg]
            auth_source="azure",  # type: ignore[call-arg]
            azure_refresh_token=azure_refresh_token,  # type: ignore[call-arg]
        )
        self.db.add(user)
        await self.db.flush()

        # Assign in-memory so _build_tokens doesn't trigger a lazy load
        user.role = default_role  # type: ignore[attr-defined]

        self.db.add(
            Profiles(
                user_id=user.id,
                fname=data["fname"],
                lname=data["lname"],
            )
        )
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

    async def authenticate_with_azure(
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
        azure_user_data = await self._get_azure_user_info(token_data["access_token"])

        user = await self._create_or_update_user(
            azure_user_data,
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
            "azure_linked": bool(getattr(user, "azure_id", None)),
            "auth_source": getattr(user, "auth_source", "email"),
            "can_unlink": getattr(user, "auth_source", "email") != "azure" or bool(user.hashed_password),
        }

    async def unlink_azure_account(self, user: User) -> None:
        if not getattr(user, "azure_id", None):
            raise ConflictException("No Azure account linked")

        if getattr(user, "auth_source", None) == "azure" and not user.hashed_password:
            raise ConflictException("Set a password before unlinking Azure so you can still log in")

        user.azure_id = None  # type: ignore[attr-defined]
        user.azure_refresh_token = None  # type: ignore[attr-defined]
        if getattr(user, "auth_source", None) == "azure":
            user.auth_source = "email"  # type: ignore[attr-defined]

        await self.db.flush()
