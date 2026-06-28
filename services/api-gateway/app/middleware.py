from fastapi import Request, HTTPException, status
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings

_SKIP_PATHS = {"/health", "/health/ready", "/docs", "/openapi.json", "/redoc"}


class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in _SKIP_PATHS:
            return await call_next(request)

        token = self._extract_token(request)
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing auth token")

        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            request.state.user_id = payload.get("sub")
            request.state.user_payload = payload
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        return await call_next(request)

    @staticmethod
    def _extract_token(request: Request) -> str | None:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            return auth[7:]
        return request.cookies.get("access_token")
