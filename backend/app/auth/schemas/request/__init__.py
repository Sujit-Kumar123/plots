from app.auth.schemas.request.auth_schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
)
from app.auth.schemas.request.password_schemas import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.auth.schemas.request.permission_schemas import (
    AssignPermissionRequest,
    CreatePermissionRequest,
    UpdatePermissionRequest,
)
from app.auth.schemas.request.profile_schemas import UpdateProfileRequest
from app.auth.schemas.request.role_schemas import (
    AssignRoleRequest,
    CreateRoleRequest,
    UpdateRoleRequest,
)

__all__ = [
    "RegisterRequest",
    "LoginRequest",
    "RefreshRequest",
    "ForgotPasswordRequest",
    "ResetPasswordRequest",
    "ChangePasswordRequest",
    "UpdateProfileRequest",
    "CreateRoleRequest",
    "UpdateRoleRequest",
    "AssignRoleRequest",
    "CreatePermissionRequest",
    "UpdatePermissionRequest",
    "AssignPermissionRequest",
]
