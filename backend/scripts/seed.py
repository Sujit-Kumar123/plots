"""
Seed script — populates roles, permissions, and sample users.
Idempotent: safe to run multiple times, skips existing records.

Usage (from backend/ directory):
    uv run python scripts/seed.py

Usage (via docker compose):
    docker compose -f docker-compose.dev.yml --profile dev-app run --no-deps --rm app \
        uv run python scripts/seed.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import Permissions, Profiles, RolePermissions, Roles, User
from app.auth.utils import hash_password
from app.database import async_session_factory

# ── Roles ─────────────────────────────────────────────────────────────────────

ROLES = [
    {"name": "Super Admin", "short_name": "superadmin", "description": "Full system access via wildcard permission"},
    {"name": "Admin", "short_name": "admin", "description": "Administrative access to users, roles, and audit"},
    {"name": "Member", "short_name": "member", "description": "Standard user access"},
]


# ── Permissions ───────────────────────────────────────────────────────────────
# Must stay in sync with backend/app/common/permissions/codes.py

PERMISSIONS = [
    # Wildcard — superadmin only, bypasses all permission checks
    {"name": "Full Access", "code": "*:*", "description": "Bypass all permission checks"},
    # Profile (self-service)
    {"name": "Profile Read", "code": "profile:read", "description": "View own profile, role, and permissions"},
    {"name": "Profile Write", "code": "profile:write", "description": "Update own profile and change password"},
    # Roles
    {"name": "Roles Read", "code": "roles:read", "description": "List and view roles"},
    {"name": "Roles Write", "code": "roles:write", "description": "Create, update, and assign roles"},
    {"name": "Roles Delete", "code": "roles:delete", "description": "Delete roles"},
    # Permissions
    {"name": "Permissions Read", "code": "permissions:read", "description": "List and view permissions"},
    {"name": "Permissions Write", "code": "permissions:write", "description": "Create, update, and assign permissions"},
    {"name": "Permissions Delete", "code": "permissions:delete", "description": "Delete permissions"},
    # Users (admin)
    {"name": "Users Read", "code": "users:read", "description": "List and view users"},
    {"name": "Users Write", "code": "users:write", "description": "Edit, activate, and deactivate users"},
    {"name": "Users Delete", "code": "users:delete", "description": "Soft-delete users"},
    # Audit
    {"name": "Audit Read", "code": "audit:read", "description": "View audit logs"},
    # Uploads
    {"name": "Uploads Read", "code": "uploads:read", "description": "View and download uploaded files"},
    {"name": "Uploads Write", "code": "uploads:write", "description": "Upload new files"},
    {"name": "Uploads Delete", "code": "uploads:delete", "description": "Delete uploaded files"},
    # Notifications
    {"name": "Notifications Write", "code": "notifications:write", "description": "Send email and SMS notifications"},
]


# ── Role → Permission assignments ─────────────────────────────────────────────

ROLE_PERMISSIONS: dict[str, list[str]] = {
    "superadmin": [
        "*:*",  # wildcard — bypasses all permission checks
    ],
    "admin": [
        "profile:read",
        "profile:write",
        "roles:read",
        "roles:write",
        "roles:delete",
        "permissions:read",
        "permissions:write",
        "permissions:delete",
        "users:read",
        "users:write",
        "users:delete",
        "audit:read",
        "uploads:read",
        "uploads:write",
        "uploads:delete",
        "notifications:write",
    ],
    "member": [
        "profile:read",
        "profile:write",
        "uploads:read",
        "uploads:write",
        "uploads:delete",
    ],
}


# ── Sample users ──────────────────────────────────────────────────────────────

USERS = [
    # ── Super Admin ───────────────────────────────────────────────────────────
    {
        "email": "superadmin@example.com",
        "password": "superadmin123",
        "role": "superadmin",
        "fname": "Super",
        "lname": "Admin",
        "company": "AIqwip",
        "designation": "Platform Owner",
    },
    # ── Admins ────────────────────────────────────────────────────────────────
    {
        "email": "admin@example.com",
        "password": "admin1234",
        "role": "admin",
        "fname": "Admin",
        "lname": "User",
        "company": "AIqwip",
        "designation": "Team Lead",
    },
    {
        "email": "priya.sharma@example.com",
        "password": "Password@123",
        "role": "admin",
        "fname": "Priya",
        "lname": "Sharma",
        "company": "AIqwip",
        "designation": "Engineering Manager",
    },
    {
        "email": "rahul.verma@example.com",
        "password": "Password@123",
        "role": "admin",
        "fname": "Rahul",
        "lname": "Verma",
        "company": "AIqwip",
        "designation": "Product Manager",
    },
    # ── Members ───────────────────────────────────────────────────────────────
    {
        "email": "member@example.com",
        "password": "member123",
        "role": "member",
        "fname": "Regular",
        "lname": "Member",
        "company": "AIqwip",
        "designation": "Developer",
    },
    {
        "email": "ananya.singh@example.com",
        "password": "Password@123",
        "role": "member",
        "fname": "Ananya",
        "lname": "Singh",
        "company": "AIqwip",
        "designation": "Frontend Developer",
    },
    {
        "email": "arjun.nair@example.com",
        "password": "Password@123",
        "role": "member",
        "fname": "Arjun",
        "lname": "Nair",
        "company": "AIqwip",
        "designation": "Backend Developer",
    },
    {
        "email": "deepika.rao@example.com",
        "password": "Password@123",
        "role": "member",
        "fname": "Deepika",
        "lname": "Rao",
        "company": "AIqwip",
        "designation": "UI/UX Designer",
    },
    {
        "email": "karan.mehta@example.com",
        "password": "Password@123",
        "role": "member",
        "fname": "Karan",
        "lname": "Mehta",
        "company": "AIqwip",
        "designation": "DevOps Engineer",
    },
    {
        "email": "sneha.kulkarni@example.com",
        "password": "Password@123",
        "role": "member",
        "fname": "Sneha",
        "lname": "Kulkarni",
        "company": "AIqwip",
        "designation": "Data Analyst",
    },
    {
        "email": "vikram.iyer@example.com",
        "password": "Password@123",
        "role": "member",
        "fname": "Vikram",
        "lname": "Iyer",
        "company": "AIqwip",
        "designation": "ML Engineer",
    },
    {
        "email": "meera.pillai@example.com",
        "password": "Password@123",
        "role": "member",
        "fname": "Meera",
        "lname": "Pillai",
        "company": "AIqwip",
        "designation": "QA Engineer",
    },
    {
        "email": "rohan.gupta@example.com",
        "password": "Password@123",
        "role": "member",
        "fname": "Rohan",
        "lname": "Gupta",
        "company": "AIqwip",
        "designation": "Full Stack Developer",
    },
    {
        "email": "tanvi.joshi@example.com",
        "password": "Password@123",
        "role": "member",
        "fname": "Tanvi",
        "lname": "Joshi",
        "company": "AIqwip",
        "designation": "Technical Writer",
    },
    {
        "email": "aditya.bose@example.com",
        "password": "Password@123",
        "role": "member",
        "fname": "Aditya",
        "lname": "Bose",
        "company": "AIqwip",
        "designation": "Cloud Architect",
    },
    {
        "email": "kavya.reddy@example.com",
        "password": "Password@123",
        "role": "member",
        "fname": "Kavya",
        "lname": "Reddy",
        "company": "AIqwip",
        "designation": "Security Engineer",
    },
    {
        "email": "nikhil.pandey@example.com",
        "password": "Password@123",
        "role": "member",
        "fname": "Nikhil",
        "lname": "Pandey",
        "company": "AIqwip",
        "designation": "Mobile Developer",
    },
    {
        "email": "pooja.desai@example.com",
        "password": "Password@123",
        "role": "member",
        "fname": "Pooja",
        "lname": "Desai",
        "company": "AIqwip",
        "designation": "Business Analyst",
    },
    {
        "email": "siddharth.mishra@example.com",
        "password": "Password@123",
        "role": "member",
        "fname": "Siddharth",
        "lname": "Mishra",
        "company": "AIqwip",
        "designation": "Platform Engineer",
    },
    {
        "email": "ishaan.malhotra@example.com",
        "password": "Password@123",
        "role": "member",
        "fname": "Ishaan",
        "lname": "Malhotra",
        "company": "AIqwip",
        "designation": "Database Administrator",
    },
    {
        "email": "riya.kapoor@example.com",
        "password": "Password@123",
        "role": "member",
        "fname": "Riya",
        "lname": "Kapoor",
        "company": "AIqwip",
        "designation": "Scrum Master",
    },
]


# ── Helpers ───────────────────────────────────────────────────────────────────


async def upsert_roles(db: AsyncSession) -> dict[str, Roles]:
    role_map: dict[str, Roles] = {}
    for data in ROLES:
        result = await db.execute(select(Roles).where(Roles.short_name == data["short_name"]))
        role = result.scalar_one_or_none()
        if not role:
            role = Roles(**data)
            db.add(role)
            await db.flush()
            print(f"  + role: {data['short_name']}")
        else:
            print(f"  ~ role exists: {data['short_name']}")
        role_map[data["short_name"]] = role
    return role_map


async def upsert_permissions(db: AsyncSession) -> dict[str, Permissions]:
    perm_map: dict[str, Permissions] = {}
    for data in PERMISSIONS:
        result = await db.execute(select(Permissions).where(Permissions.code == data["code"]))
        perm = result.scalar_one_or_none()
        if not perm:
            perm = Permissions(**data)
            db.add(perm)
            await db.flush()
            print(f"  + permission: {data['code']}")
        else:
            print(f"  ~ permission exists: {data['code']}")
        perm_map[data["code"]] = perm
    return perm_map


async def assign_permissions(
    db: AsyncSession,
    role_map: dict[str, Roles],
    perm_map: dict[str, Permissions],
) -> None:
    for short_name, codes in ROLE_PERMISSIONS.items():
        role = role_map[short_name]
        for code in codes:
            perm = perm_map[code]
            result = await db.execute(
                select(RolePermissions).where(
                    RolePermissions.role_id == role.id,
                    RolePermissions.permission_id == perm.id,
                )
            )
            if not result.scalar_one_or_none():
                db.add(RolePermissions(role_id=role.id, permission_id=perm.id))
                print(f"  + {short_name} <- {code}")
            else:
                print(f"  ~ {short_name} <- {code} already assigned")


async def upsert_users(db: AsyncSession, role_map: dict[str, Roles]) -> None:
    for data in USERS:
        result = await db.execute(select(User).where(User.email == data["email"]))
        user = result.scalar_one_or_none()
        if not user:
            role = role_map[data["role"]]
            user = User(
                email=data["email"],
                hashed_password=hash_password(data["password"]),
                is_active=True,
                is_verified=True,
                role_id=role.id,
            )
            db.add(user)
            await db.flush()
            profile = Profiles(
                user_id=user.id,
                fname=data.get("fname"),
                lname=data.get("lname"),
                company=data.get("company"),
                designation=data.get("designation"),
            )
            db.add(profile)
            await db.flush()
            print(f"  + user: {data['email']} ({data['role']})")
        else:
            print(f"  ~ user exists: {data['email']}")


# ── Main ──────────────────────────────────────────────────────────────────────


async def seed() -> None:
    async with async_session_factory() as db:
        try:
            print("\n[seed] Roles...")
            role_map = await upsert_roles(db)

            print("\n[seed] Permissions...")
            perm_map = await upsert_permissions(db)

            print("\n[seed] Role -> Permission assignments...")
            await assign_permissions(db, role_map, perm_map)

            print("\n[seed] Users...")
            await upsert_users(db, role_map)

            await db.commit()
            print("\n[seed] Done.\n")

        except Exception as e:
            await db.rollback()
            print(f"\n[seed] Failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed())
