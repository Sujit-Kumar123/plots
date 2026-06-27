import pytest
from httpx import AsyncClient

from app.auth.models import User


@pytest.mark.asyncio
async def test_password_reset_request(async_client: AsyncClient, test_user: User):
    response = await async_client.post(
        "/api/auth/forgot-password",
        json={"email": test_user.email},
    )
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_password_reset_unknown_email(async_client: AsyncClient):
    """Should still return 200 to not reveal email existence."""
    response = await async_client.post(
        "/api/auth/forgot-password",
        json={"email": "nobody@example.com"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_password_reset_confirm_invalid_token(async_client: AsyncClient):
    response = await async_client.post(
        "/api/auth/reset-password",
        json={"token": "invalid-token", "new_password": "NewPass123!"},
    )
    assert response.status_code in (400, 422)
