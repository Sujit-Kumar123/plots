import logging

from fastapi import APIRouter, Depends, Query, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.auth.service import GoogleAuthService
from app.auth.utils.cookies import set_auth_cookies
from app.common.responses import success_response
from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth/google", tags=["google-auth"])


@router.get("")
async def google_login():
    """Redirect browser to Google consent screen."""
    from app.database import async_session_factory

    async with async_session_factory() as db:
        svc = GoogleAuthService(db)
        auth_url, _ = svc.generate_auth_url()
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def google_callback(
    request: Request,
    response: Response,
    code: str = Query(...),
    state: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Google redirects here after user grants access."""
    from app.common.exceptions import UnauthorizedException
    from app.config import settings

    ip = request.client.host if request.client else None
    try:
        svc = GoogleAuthService(db)
        user, access_token, refresh_token = await svc.authenticate_with_google(code, ip)
        set_auth_cookies(response, access_token, refresh_token)
        redirect = RedirectResponse(url=f"{settings.frontend_url}/dashboard")
        set_auth_cookies(redirect, access_token, refresh_token)
        return redirect
    except UnauthorizedException as exc:
        return RedirectResponse(url=f"{settings.frontend_url}/login?error={exc.message}")
    except Exception:
        logger.error("Google OAuth callback unexpected error", exc_info=True)
        return RedirectResponse(url=f"{settings.frontend_url}/login?error=auth_failed")


@router.get("/status")
async def google_status(current_user: User = Depends(get_current_user)):
    """Return Google link status for the current user."""
    from app.database import async_session_factory

    async with async_session_factory() as db:
        svc = GoogleAuthService(db)
        return success_response(data=svc.get_oauth_status(current_user))


@router.delete("/unlink")
async def google_unlink(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Unlink Google account from the current user."""
    svc = GoogleAuthService(db)
    await svc.unlink_google_account(current_user)
    return success_response(message="Google account unlinked")
