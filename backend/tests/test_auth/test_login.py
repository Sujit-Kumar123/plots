import pytest
from httpx import AsyncClient

from app.auth.models import User


@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient, test_user: User):
    response = await async_client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": "TestPass123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["access_token"]
    assert data["data"]["refresh_token"]


@pytest.mark.asyncio
async def test_login_wrong_password(async_client: AsyncClient, test_user: User):
    response = await async_client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": "WrongPass123!"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_email(async_client: AsyncClient):
    response = await async_client.post(
        "/api/auth/login",
        json={"email": "nobody@example.com", "password": "Whatever123!"},
    )
    assert response.status_code == 401
