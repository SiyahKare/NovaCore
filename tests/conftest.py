"""
NovaCore Test Configuration
"""
import asyncio
from collections.abc import AsyncGenerator
from decimal import Decimal

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.core.db import get_session
from app.core.security import create_access_token
from app.main import app

# Test database URL (in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session_factory = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session_factory() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(test_session) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with overridden dependencies."""

    async def override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(test_session):
    """Create a test user."""
    from app.identity.models import User

    user = User(
        telegram_id=123456789,
        username="testuser",
        display_name="Test User",
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user_token(test_user):
    """Create JWT token for test user."""
    return create_access_token(user_id=test_user.id)


@pytest_asyncio.fixture
async def admin_user(test_session):
    """Create an admin user."""
    from app.identity.models import User

    user = User(
        telegram_id=999999999,
        username="admin",
        display_name="Admin User",
        is_admin=True,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_token(admin_user):
    """Create JWT token for admin user."""
    return create_access_token(user_id=admin_user.id)


@pytest_asyncio.fixture
async def test_account(test_session, test_user):
    """Create a test account with balance."""
    from app.wallet.models import Account

    account = Account(
        user_id=test_user.id,
        token="NCR",
        balance=Decimal("1000"),
    )
    test_session.add(account)
    await test_session.commit()
    await test_session.refresh(account)
    return account


@pytest_asyncio.fixture
async def test_agency(test_session, test_user):
    """Create a test agency."""
    from app.agency.models import Agency, AgencyOperator, OperatorRole

    agency = Agency(
        name="Test Agency",
        slug="test-agency",
        owner_user_id=test_user.id,
    )
    test_session.add(agency)
    await test_session.flush()

    operator = AgencyOperator(
        agency_id=agency.id,
        user_id=test_user.id,
        role=OperatorRole.PATRONICE,
    )
    test_session.add(operator)
    await test_session.commit()
    await test_session.refresh(agency)

    return agency


@pytest_asyncio.fixture
async def test_performer(test_session, test_agency):
    """Create a test performer."""
    from app.agency.models import Performer

    performer = Performer(
        agency_id=test_agency.id,
        display_name="Test Performer",
        handle="test_performer",
    )
    test_session.add(performer)
    await test_session.commit()
    await test_session.refresh(performer)
    return performer

