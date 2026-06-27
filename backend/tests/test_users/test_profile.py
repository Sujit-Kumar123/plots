import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_me(authenticated_client: AsyncClient):
    response = await authenticated_client.get("/api/profile/me")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"]
    assert data["data"]["profile"] is not None


@pytest.mark.asyncio
async def test_update_profile(authenticated_client: AsyncClient):
    response = await authenticated_client.patch(
        "/api/profile/me",
        json={"fname": "Updated", "lname": "Name"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_change_password(authenticated_client: AsyncClient):
    response = await authenticated_client.put(
        "/api/profile/me/password",
        json={"current_password": "TestPass123!", "new_password": "NewPass456!"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_change_password_wrong_current(authenticated_client: AsyncClient):
    response = await authenticated_client.put(
        "/api/profile/me/password",
        json={"current_password": "WrongPass!", "new_password": "NewPass456!"},
    )
    assert response.status_code in (400, 422)


@pytest.mark.asyncio
async def test_get_me_unauthenticated(async_client: AsyncClient):
    response = await async_client.get("/api/profile/me")
    assert response.status_code == 401
