from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    def __init__(self, status_code: int, message: str, errors: list | None = None):
        self.status_code = status_code
        self.message = message
        self.errors = errors


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(status_code=404, message=message)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Not authenticated"):
        super().__init__(status_code=401, message=message)


class ForbiddenException(AppException):
    def __init__(self, message: str = "Not authorized"):
        super().__init__(status_code=403, message=message)


class ValidationException(AppException):
    def __init__(self, message: str = "Validation error", errors: list | None = None):
        super().__init__(status_code=422, message=message, errors=errors)


class ConflictException(AppException):
    def __init__(self, message: str = "Conflict"):
        super().__init__(status_code=409, message=message)


class InternalException(AppException):
    def __init__(self, message: str = "An internal error occurred"):
        super().__init__(status_code=500, message=message)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "data": None,
                "message": exc.message,
                "errors": exc.errors,
            },
        )
