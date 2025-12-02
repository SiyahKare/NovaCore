"""
NovaCore Wallet Tests
"""
from decimal import Decimal

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_my_balance(client: AsyncClient, test_user, test_user_token, test_account):
    """Test get current user's balance."""
    response = await client.get(
        "/api/v1/wallet/me",
        headers={"Authorization": f"Bearer {test_user_token}"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["user_id"] == test_user.id
    assert data["token"] == "NCR"
    assert Decimal(data["balance"]) == Decimal("1000")


@pytest.mark.asyncio
async def test_get_user_balance(client: AsyncClient, test_user, test_account):
    """Test get user balance by ID."""
    response = await client.get(f"/api/v1/wallet/balance/{test_user.id}")

    assert response.status_code == 200
    data = response.json()

    assert Decimal(data["balance"]) == Decimal("1000")


@pytest.mark.asyncio
async def test_create_transaction_spend(client: AsyncClient, test_user, test_account):
    """Test create spend transaction."""
    response = await client.post(
        "/api/v1/wallet/tx",
        json={
            "user_id": test_user.id,
            "amount": "100",
            "type": "spend",
            "source_app": "flirt",
            "metadata": {"event_type": "COIN_SPENT"},
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert Decimal(data["amount"]) == Decimal("100")
    assert data["type"] == "spend"
    assert Decimal(data["balance_after"]) == Decimal("900")


@pytest.mark.asyncio
async def test_create_transaction_earn(client: AsyncClient, test_user, test_account):
    """Test create earn transaction."""
    response = await client.post(
        "/api/v1/wallet/tx",
        json={
            "user_id": test_user.id,
            "amount": "50",
            "type": "earn",
            "source_app": "onlyvips",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert Decimal(data["balance_after"]) == Decimal("1050")


@pytest.mark.asyncio
async def test_create_transaction_insufficient_balance(client: AsyncClient, test_user, test_account):
    """Test spend with insufficient balance."""
    response = await client.post(
        "/api/v1/wallet/tx",
        json={
            "user_id": test_user.id,
            "amount": "2000",  # More than balance
            "type": "spend",
            "source_app": "flirt",
        },
    )

    assert response.status_code == 400
    assert "Insufficient balance" in response.json()["detail"]


@pytest.mark.asyncio
async def test_transfer(client: AsyncClient, test_user, test_user_token, test_account, test_session):
    """Test transfer between users."""
    from app.identity.models import User

    # Create recipient user
    recipient = User(
        telegram_id=987654321,
        username="recipient",
    )
    test_session.add(recipient)
    await test_session.commit()
    await test_session.refresh(recipient)

    response = await client.post(
        "/api/v1/wallet/transfer",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={
            "to_user_id": recipient.id,
            "amount": "100",
            "note": "Test transfer",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["from_user_id"] == test_user.id
    assert data["to_user_id"] == recipient.id
    assert Decimal(data["amount"]) == Decimal("100")
    assert Decimal(data["from_balance_after"]) == Decimal("900")
    assert Decimal(data["to_balance_after"]) == Decimal("100")


@pytest.mark.asyncio
async def test_get_my_transactions(client: AsyncClient, test_user, test_user_token, test_account):
    """Test get transaction history."""
    # First create some transactions
    await client.post(
        "/api/v1/wallet/tx",
        json={
            "user_id": test_user.id,
            "amount": "50",
            "type": "spend",
            "source_app": "flirt",
        },
    )

    response = await client.get(
        "/api/v1/wallet/me/transactions",
        headers={"Authorization": f"Bearer {test_user_token}"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["total"] >= 1
    assert len(data["transactions"]) >= 1

