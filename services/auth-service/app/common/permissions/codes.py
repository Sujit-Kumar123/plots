"""
All permission codes used across the API.
Format: "resource:action"

Seed these into the database via POST /api/auth/permissions.
Superadmin role can be granted "*:*" to bypass all checks.
"""

PERMISSIONS: list[str] = [
    # Profile (self-service)
    "profile:read",
    "profile:write",
    # Roles
    "roles:read",
    "roles:write",
    "roles:delete",
    # Permissions
    "permissions:read",
    "permissions:write",
    "permissions:delete",
    # Users (admin)
    "users:read",
    "users:write",
    "users:delete",
    # Audit
    "audit:read",
    # Uploads
    "uploads:read",
    "uploads:write",
    "uploads:delete",
    # Notifications
    "notifications:write",
    # Plot sheets
    "sheets:read",
    "sheets:write",
    "sheets:delete",
]
