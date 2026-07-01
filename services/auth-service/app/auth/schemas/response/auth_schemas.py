from pydantic import BaseModel

from app.auth.schemas.response.user_schemas import UserWithProfileResponse


class AuthTokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    user: UserWithProfileResponse
    tokens: AuthTokens


class LoginResponse(BaseModel):
    user: UserWithProfileResponse
    tokens: AuthTokens
