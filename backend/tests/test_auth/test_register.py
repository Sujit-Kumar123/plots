import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(async_client: AsyncClient):
    response = await async_client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "StrongPass123!",
            "first_name": "New",
            "last_name": "User",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["user"]["email"] == "newuser@example.com"
    assert data["data"]["tokens"]["access_token"]
    assert data["data"]["tokens"]["refresh_token"]


@pytest.mark.asyncio
async def test_register_duplicate_email(async_client: AsyncClient, test_user):
    response = await async_client.post(
        "/api/auth/register",
        json={
            "email": test_user.email,
            "password": "StrongPass123!",
        },
    )
    assert response.status_code == 409
    assert response.json()["success"] is False


@pytest.mark.asyncio
async def test_register_weak_password(async_client: AsyncClient):
    response = await async_client.post(
        "/api/auth/register",
        json={
            "email": "weakpass@example.com",
            "password": "short",
        },
    )
    assert response.status_code == 422
