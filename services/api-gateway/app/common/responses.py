from typing import Any

from pydantic import BaseModel


class ApiResponse(BaseModel):
    success: bool = True
    data: Any = None
    message: str | None = None
    errors: list | None = None


def success_response(data: Any = None, message: str | None = None) -> dict:
    return {
        "success": True,
        "data": data,
        "message": message,
        "errors": None,
    }
