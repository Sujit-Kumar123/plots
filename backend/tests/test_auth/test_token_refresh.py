import pytest
from httpx import AsyncClient

from app.auth.models import User
from app.auth.utils import create_refresh_token


@pytest.mark.asyncio
async def test_refresh_success(async_client: AsyncClient, test_user: User):
    role_name = test_user.role.short_name if test_user.role else "member"
    refresh_token = create_refresh_token(str(test_user.id), role_name)
    response = await async_client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["access_token"]


@pytest.mark.asyncio
async def test_refresh_invalid_token(async_client: AsyncClient):
    response = await async_client.post(
        "/api/auth/refresh",
        json={"refresh_token": "invalid-token"},
    )
    assert response.status_code == 401
