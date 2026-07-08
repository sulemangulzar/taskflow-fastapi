"""
Pytest configuration and fixtures for TaskFlow API tests.

Uses an in-memory SQLite database (via aiosqlite) so tests run without
a real PostgreSQL or Redis instance.
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from app.api.dependencies import get_session
from app.core.limiter import limiter
from app.db.redis import token_blocklist
from app.main import app

# ---------------------------------------------------------------------------
# Disable Rate Limiter for tests
# ---------------------------------------------------------------------------
limiter.enabled = False

# ---------------------------------------------------------------------------
# In-memory async SQLite engine
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ---------------------------------------------------------------------------
# Override DB session
# ---------------------------------------------------------------------------
async def override_get_session():
    async with TestingSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture(autouse=True)
async def create_tables():
    """Create all tables once per test session."""
    # Import models so SQLModel knows about them
    from app.models.projects import Project  # noqa: F401
    from app.models.task import Task  # noqa: F401
    from app.models.user import User  # noqa: F401

    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    """Return a test HTTP client with overridden DB session."""
    app.dependency_overrides[get_session] = override_get_session

    # Patch Redis blocklist to be a no-op for tests
    from unittest.mock import AsyncMock, patch

    # Also patch celery send_email to be a no-op
    from app.celery_tasks import send_email

    with (
        patch.object(token_blocklist, "exists", new=AsyncMock(return_value=0)),
        patch.object(token_blocklist, "set", new=AsyncMock(return_value=True)),
        patch.object(send_email, "delay", return_value=True),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def registered_user(client: AsyncClient) -> dict:
    """Register a test user and return the response payload."""
    payload = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "secret123",
    }
    resp = await client.post("/auth/v1/signup", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest_asyncio.fixture
async def auth_tokens(client: AsyncClient, registered_user) -> dict:
    """Log in the test user and return access + refresh tokens."""
    resp = await client.post(
        "/auth/v1/login",
        data={"username": "test@example.com", "password": "secret123"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


@pytest.fixture
def auth_headers(auth_tokens: dict) -> dict:
    """Return Authorization headers for authenticated requests."""
    return {"Authorization": f"Bearer {auth_tokens['access_token']}"}
