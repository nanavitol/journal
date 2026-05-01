import sys
from pathlib import Path

# Add the parent directory to the path so that vosvod_backend can be imported
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

@pytest.fixture
async def async_client():
    """Async HTTP client for testing."""
    from httpx import AsyncClient, ASGITransport
    from app.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

@pytest.fixture
async def db_session():
    """Database session for tests with automatic rollback."""
    from app.core.database import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        # Start a nested transaction for test isolation
        await session.begin_nested()
        yield session
        # Rollback to avoid persisting test data
        await session.rollback()
        await session.close()