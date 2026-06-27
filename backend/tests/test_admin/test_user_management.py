import pytest
from httpx import AsyncClient

from app.auth.models import User


@pytest.mark.asyncio
async def test_list_users_as_admin(admin_client: AsyncClient):
    response = await admin_client.get("/api/admin/users")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "items" in data["data"]
    assert "total" in data["data"]


@pytest.mark.asyncio
async def test_list_users_as_member(authenticated_client: AsyncClient):
    response = await authenticated_client.get("/api/admin/users")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_user_detail(admin_client: AsyncClient, test_user: User):
    response = await admin_client.get(f"/api/admin/users/{test_user.id}")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_deactivate_user(admin_client: AsyncClient, test_user: User):
    response = await admin_client.post(f"/api/admin/users/{test_user.id}/deactivate")
    assert response.status_code == 200
    assert response.json()["data"]["is_active"] is False


@pytest.mark.asyncio
async def test_activate_user(admin_client: AsyncClient, test_user: User):
    response = await admin_client.post(f"/api/admin/users/{test_user.id}/activate")
    assert response.status_code == 200
    assert response.json()["data"]["is_active"] is True
