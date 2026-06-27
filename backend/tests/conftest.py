import asyncio
import uuid
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.auth.models import Permissions, Profiles, RolePermissions, Roles, User
from app.auth.utils import create_access_token, hash_password
from app.config import settings
from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = settings.database_url.rsplit("/", 1)[0] + "/mvp_test_db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

# Permissions needed by tests, grouped by role
_MEMBER_PERMISSIONS = ["profile:read", "profile:write", "uploads:read", "uploads:write", "uploads:delete"]
_ADMIN_PERMISSIONS = [
    "profile:read",
    "profile:write",
    "users:read",
    "users:write",
    "users:delete",
    "roles:read",
    "roles:write",
    "roles:delete",
    "permissions:read",
    "permissions:write",
    "permissions:delete",
    "audit:read",
    "uploads:read",
    "uploads:write",
    "uploads:delete",
    "notifications:write",
]
_ALL_PERMISSIONS = [
    ("profile:read", "Profile Read"),
    ("profile:write", "Profile Write"),
    ("users:read", "Users Read"),
    ("users:write", "Users Write"),
    ("users:delete", "Users Delete"),
    ("roles:read", "Roles Read"),
    ("roles:write", "Roles Write"),
    ("roles:delete", "Roles Delete"),
    ("permissions:read", "Permissions Read"),
    ("permissions:write", "Permissions Write"),
    ("permissions:delete", "Permissions Delete"),
    ("audit:read", "Audit Read"),
    ("uploads:read", "Uploads Read"),
    ("uploads:write", "Uploads Write"),
    ("uploads:delete", "Uploads Delete"),
    ("notifications:write", "Notifications Write"),
]


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed roles and permissions needed by test fixtures (committed, so they
    # survive per-test session rollbacks).
    async with test_session_factory() as session:
        async with session.begin():
            # Upsert all permissions
            perms: dict[str, Permissions] = {}
            for code, name in _ALL_PERMISSIONS:
                result = await session.execute(select(Permissions).where(Permissions.code == code))
                perm = result.scalar_one_or_none()
                if not perm:
                    perm = Permissions(name=name, code=code)
                    session.add(perm)
                    await session.flush()
                perms[code] = perm

            # Member role
            result = await session.execute(select(Roles).where(Roles.short_name == "member"))
            member_role = result.scalar_one_or_none()
            if not member_role:
                member_role = Roles(name="Member", short_name="member")
                session.add(member_role)
                await session.flush()
                for code in _MEMBER_PERMISSIONS:
                    session.add(RolePermissions(role_id=member_role.id, permission_id=perms[code].id))

            # Admin role
            result = await session.execute(select(Roles).where(Roles.short_name == "admin"))
            admin_role = result.scalar_one_or_none()
            if not admin_role:
                admin_role = Roles(name="Admin", short_name="admin")
                session.add(admin_role)
                await session.flush()
                for code in _ADMIN_PERMISSIONS:
                    session.add(RolePermissions(role_id=admin_role.id, permission_id=perms[code].id))

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with test_session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def async_client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db: AsyncSession) -> User:
    result = await db.execute(select(Roles).where(Roles.short_name == "member"))
    role = result.scalar_one()
    user = User(
        email=f"testuser-{uuid.uuid4().hex[:8]}@example.com",
        hashed_password=hash_password("TestPass123!"),
        role_id=role.id,
        is_active=True,
        is_verified=True,
    )
    user.role = role  # populate relationship in-memory for fixtures that read user.role
    db.add(user)
    await db.flush()
    profile = Profiles(user_id=user.id, fname="Test", lname="User")
    db.add(profile)
    await db.flush()
    return user


@pytest.fixture
async def admin_user(db: AsyncSession) -> User:
    result = await db.execute(select(Roles).where(Roles.short_name == "admin"))
    role = result.scalar_one()
    user = User(
        email=f"admin-{uuid.uuid4().hex[:8]}@example.com",
        hashed_password=hash_password("AdminPass123!"),
        role_id=role.id,
        is_active=True,
        is_verified=True,
    )
    user.role = role
    db.add(user)
    await db.flush()
    profile = Profiles(user_id=user.id, fname="Admin", lname="User")
    db.add(profile)
    await db.flush()
    return user


@pytest.fixture
async def authenticated_client(async_client: AsyncClient, test_user: User) -> AsyncClient:
    role_name = test_user.role.short_name if test_user.role else "member"
    token = create_access_token(str(test_user.id), role_name)
    async_client.headers["Authorization"] = f"Bearer {token}"
    return async_client


@pytest.fixture
async def admin_client(async_client: AsyncClient, admin_user: User) -> AsyncClient:
    role_name = admin_user.role.short_name if admin_user.role else "admin"
    token = create_access_token(str(admin_user.id), role_name)
    async_client.headers["Authorization"] = f"Bearer {token}"
    return async_client
