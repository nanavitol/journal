import pytest
import asyncio
import uuid
from datetime import date, time
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash, verify_password
from app.models.users import User
from app.models.cities import City
from app.models.posts import Post
from app.models.shifts import Shift
from app.models.shift_assignments import ShiftAssignment
from app.models.journal_entries import JournalEntry

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

@pytest.fixture(scope="function")
async def async_client():
    """Async HTTP client for testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

@pytest.fixture(scope="function")
async def db_session():
    """Database session for tests with automatic rollback."""
    async with AsyncSessionLocal() as session:
        # Start a nested transaction for test isolation
        await session.begin_nested()
        yield session
        # Rollback to avoid persisting test data
        await session.rollback()
        await session.close()

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------

async def get_admin_token(client):
    """Helper to get admin token."""
    response = await client.post(
        "/auth/login",
        json={"login": "VodalchukMNK", "password": "Vodalchuk123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]

async def get_worker_token(client):
    """Helper to get worker token."""
    response = await client.post(
        "/auth/login",
        json={"login": "MorozovMNK", "password": "Morozov123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]

def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}

# ----------------------------------------------------------------------
# Tests without authentication
# ----------------------------------------------------------------------

@pytest.mark.asyncio
async def test_root_without_auth(async_client):
    resp = await async_client.get("/")
    assert resp.status_code == 200
    assert "Вахтенный журнал" in resp.json()["message"]

@pytest.mark.asyncio
async def test_login_without_auth(async_client):
    resp = await async_client.post(
        "/auth/login",
        json={"login": "nonexistent", "password": "wrong"},
    )
    assert resp.status_code == 401

# ----------------------------------------------------------------------
# Authentication tests
# ----------------------------------------------------------------------

@pytest.mark.asyncio
async def test_admin_login(async_client):
    token = await get_admin_token(async_client)
    assert token is not None
    assert len(token) > 0

@pytest.mark.asyncio
async def test_worker_login(async_client):
    token = await get_worker_token(async_client)
    assert token is not None
    assert len(token) > 0

@pytest.mark.asyncio
async def test_login_wrong_password(async_client):
    resp = await async_client.post(
        "/auth/login",
        json={"login": "VodalchukMNK", "password": "wrongpassword"},
    )
    assert resp.status_code == 401

@pytest.mark.asyncio
async def test_login_nonexistent_user(async_client):
    resp = await async_client.post(
        "/auth/login",
        json={"login": "NonexistentUser", "password": "password"},
    )
    assert resp.status_code == 401

# ----------------------------------------------------------------------
# Change password tests
# ----------------------------------------------------------------------

@pytest.mark.asyncio
async def test_worker_change_password(async_client):
    # First login as worker
    token = await get_worker_token(async_client)
    headers = auth_headers(token)
    
    # Change password
    resp = await async_client.post(
        "/auth/change-password",
        json={"old_password": "Morozov123", "new_password": "NewPass123"},
        headers=headers,
    )
    assert resp.status_code == 200
    
    # Login with new password
    resp = await async_client.post(
        "/auth/login",
        json={"login": "MorozovMNK", "password": "NewPass123"},
    )
    assert resp.status_code == 200

# ----------------------------------------------------------------------
# User management tests (admin only)
# ----------------------------------------------------------------------

@pytest.mark.asyncio
async def test_admin_create_user(async_client, db_session):
    token = await get_admin_token(async_client)
    headers = auth_headers(token)
    
    # Create a unique user
    unique_login = f"NewUser{uuid.uuid4().hex[:8]}MNK"
    new_user = {
        "email": f"newuser{uuid.uuid4().hex[:8]}@example.com",
        "login": unique_login,
        "password": "NewPass123",
        "full_name": "Новый Пользователь Местный",
        "city_id": 1,
        "role": "worker",
        "rank": "сержант",
        "phone": "89001112233",
    }
    resp = await async_client.post("/admin/users", json=new_user, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["login"] == unique_login
    assert resp.json()["role"] == "worker"

@pytest.mark.asyncio
async def test_admin_get_user(async_client, db_session):
    token = await get_admin_token(async_client)
    headers = auth_headers(token)
    
    # Get admin user (ID 1 should exist from init_data)
    resp = await async_client.get("/admin/users/1", headers=headers)
    assert resp.status_code == 200
    assert "Водальчук" in resp.json()["full_name"]

@pytest.mark.asyncio
async def test_worker_cannot_create_user(async_client):
    token = await get_worker_token(async_client)
    headers = auth_headers(token)
    
    new_user = {
        "email": "hacker@example.com",
        "login": "HackerMNK",
        "password": "HackPass123",
        "full_name": "Хакер Местный",
        "city_id": 1,
        "role": "admin",
    }
    resp = await async_client.post("/admin/users", json=new_user, headers=headers)
    assert resp.status_code == 403  # Forbidden

# ----------------------------------------------------------------------
# City management tests (admin only)
# ----------------------------------------------------------------------

@pytest.mark.asyncio
async def test_admin_create_city(async_client, db_session):
    token = await get_admin_token(async_client)
    headers = auth_headers(token)
    
    city_data = {"name": "Новый Город"}
    resp = await async_client.post("/admin/cities", json=city_data, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["name"] == "Новый Город"

# ----------------------------------------------------------------------
# Worker endpoints tests
# ----------------------------------------------------------------------

@pytest.mark.asyncio
async def test_worker_get_own_profile(async_client):
    token = await get_worker_token(async_client)
    headers = auth_headers(token)
    
    resp = await async_client.get("/users/me", headers=headers)
    assert resp.status_code == 200
    assert "Морозов" in resp.json()["full_name"]

@pytest.mark.asyncio
async def test_worker_get_colleagues(async_client):
    token = await get_worker_token(async_client)
    headers = auth_headers(token)
    
    resp = await async_client.get("/users/colleagues", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

# ----------------------------------------------------------------------
# Database integrity tests
# ----------------------------------------------------------------------

@pytest.mark.asyncio
async def test_password_hashed_not_plaintext(db_session):
    """Verify that passwords are stored as hashes, not plain text."""
    result = await db_session.execute(select(User).where(User.login == "VodalchukMNK"))
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.password_hash != "Vodalchuk123"
    assert verify_password("Vodalchuk123", user.password_hash)

@pytest.mark.asyncio
async def test_unique_login_constraint(db_session):
    """Test that login field is unique."""
    from sqlalchemy.exc import IntegrityError
    
    unique_login = f"UniqueLogin{uuid.uuid4().hex[:8]}MNK"
    duplicate_user = User(
        id=uuid.uuid4(),
        email=f"unique{uuid.uuid4().hex[:8]}@example.com",
        login=unique_login,
        password_hash=get_password_hash("pass"),
        full_name="Уникальный Логин",
        role="worker",
    )
    db_session.add(duplicate_user)
    await db_session.commit()
    
    # Try to create another user with same login
    duplicate_user2 = User(
        id=uuid.uuid4(),
        email=f"unique2{uuid.uuid4().hex[:8]}@example.com",
        login=unique_login,  # Duplicate login
        password_hash=get_password_hash("pass"),
        full_name="Дубликат Логина",
        role="worker",
    )
    db_session.add(duplicate_user2)
    try:
        await db_session.commit()
        assert False, "Should have raised IntegrityError"
    except IntegrityError:
        await db_session.rollback()
        assert True