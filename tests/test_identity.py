"""
NovaCore Identity Tests
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_telegram_auth(client: AsyncClient):
    """Test Telegram authentication."""
    response = await client.post(
        "/api/v1/auth/telegram/verify",
        json={
            "telegram_id": 111222333,
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["telegram_id"] == 111222333
    assert data["user"]["username"] == "newuser"


@pytest.mark.asyncio
async def test_telegram_auth_existing_user(client: AsyncClient, test_user):
    """Test Telegram auth for existing user."""
    response = await client.post(
        "/api/v1/auth/telegram/verify",
        json={
            "telegram_id": test_user.telegram_id,
            "username": test_user.username,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["user"]["id"] == test_user.id


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, test_user, test_user_token):
    """Test get current user."""
    response = await client.get(
        "/api/v1/me",
        headers={"Authorization": f"Bearer {test_user_token}"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == test_user.id
    assert data["telegram_id"] == test_user.telegram_id
    assert data["username"] == test_user.username


@pytest.mark.asyncio
async def test_get_me_unauthorized(client: AsyncClient):
    """Test get current user without auth."""
    response = await client.get("/api/v1/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_me(client: AsyncClient, test_user, test_user_token):
    """Test update current user."""
    response = await client.patch(
        "/api/v1/me",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={
            "display_name": "Updated Name",
            "ton_wallet": "EQxxx",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["display_name"] == "Updated Name"
    assert data["ton_wallet"] == "EQxxx"


@pytest.mark.asyncio
async def test_get_user_by_id(client: AsyncClient, test_user):
    """Test get user by ID."""
    response = await client.get(f"/api/v1/users/{test_user.id}")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == test_user.id


@pytest.mark.asyncio
async def test_get_user_not_found(client: AsyncClient):
    """Test get non-existent user."""
    response = await client.get("/api/v1/users/99999")

    assert response.status_code == 404

