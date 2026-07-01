from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.auth.schemas import (
    AuthTokens,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    ResetPasswordRequest,
    UserWithProfileResponse,
)
from app.auth.service import AuthService
from app.auth.utils.cookies import clear_auth_cookies, set_auth_cookies
from app.common.responses import success_response
from app.config import settings
from app.database import get_db
from app.notifications.email import send_email

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _email_auth_enabled() -> None:
    """Dependency — raises 503 when email/password auth is disabled via AUTH_EMAIL_ENABLED=false."""
    if not settings.auth_email_enabled:
        raise HTTPException(
            status_code=503,
            detail="Email/password authentication is not enabled on this server.",
        )


def _parse_device_type(user_agent: str) -> str:
    ua = user_agent.lower()
    if any(k in ua for k in ("mobile", "android", "iphone")):
        return "mobile"
    if any(k in ua for k in ("tablet", "ipad")):
        return "tablet"
    return "web"


@router.post("/register", dependencies=[Depends(_email_auth_enabled)])
async def register(body: RegisterRequest, request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    ip = request.client.host if request.client else None
    svc = AuthService(db)
    user, access_token, refresh_token = await svc.register_user(body.email, body.password, body.fname, body.lname, ip)
    user = await svc.get_user_with_relations(user.id)
    set_auth_cookies(response, access_token, refresh_token)
    return success_response(
        data=RegisterResponse(
            user=UserWithProfileResponse.model_validate(user),
            tokens=AuthTokens(access_token=access_token, refresh_token=refresh_token),
        ).model_dump()
    )


@router.post("/login", dependencies=[Depends(_email_auth_enabled)])
async def login(body: LoginRequest, request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    ip = request.client.host if request.client else None
    device_type = _parse_device_type(request.headers.get("user-agent", ""))
    svc = AuthService(db)
    user, access_token, refresh_token = await svc.login_user(body.email, body.password, ip, device_type)
    user = await svc.get_user_with_relations(user.id)
    set_auth_cookies(response, access_token, refresh_token)
    return success_response(
        data=LoginResponse(
            user=UserWithProfileResponse.model_validate(user),
            tokens=AuthTokens(access_token=access_token, refresh_token=refresh_token),
        ).model_dump()
    )


@router.post("/refresh")
async def refresh(body: RefreshRequest, response: Response, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    access_token, refresh_token = await svc.refresh_access_token(body.refresh_token)
    set_auth_cookies(response, access_token, refresh_token)
    return success_response(data=AuthTokens(access_token=access_token, refresh_token=refresh_token).model_dump())


@router.post("/logout")
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = AuthService(db)
    await svc.logout_user(current_user.id)
    clear_auth_cookies(response)
    return success_response(message="Logged out")


@router.post("/forgot-password", dependencies=[Depends(_email_auth_enabled)])
async def forgot_password(body: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    result = await svc.request_password_reset(body.email)
    dev_data = None
    if result:
        raw_token, _ = result
        reset_url = f"{settings.frontend_url}/reset-password?token={raw_token}"
        await send_email(
            to=body.email,
            subject="Reset your password",
            template_name="password_reset",
            context={"reset_url": reset_url},
        )
        if settings.debug:
            dev_data = {"reset_url": reset_url}
    return success_response(
        data=dev_data,
        message="If the email exists, a reset link has been sent",
    )


@router.post("/reset-password", dependencies=[Depends(_email_auth_enabled)])
async def reset_password(body: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    await svc.confirm_password_reset(body.token, body.new_password)
    return success_response(message="Password has been reset")


@router.post("/change-password", dependencies=[Depends(_email_auth_enabled)])
async def change_password(
    body: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = AuthService(db)
    await svc.change_password(current_user.id, body.current_password, body.new_password)
    return success_response(message="Password changed")
