import pytest
from app.users.repository import UserRepository
from app.users.schemas import UserCreate
from app.core.security import verify_password


@pytest.mark.asyncio(loop_scope="session")
async def test_create_user(db_session):
    """Test creating a user via repository."""
    repo = UserRepository(db_session)
    user_data = UserCreate(email="newuser@example.com", password="password123")

    created_user = await repo.create(user_data)

    assert created_user.id is not None
    assert created_user.email == "newuser@example.com"
    assert verify_password("password123", created_user.hashed_password)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_nonexistent_user_by_email(db_session):
    """Test getting a nonexistent user by email."""
    repo = UserRepository(db_session)

    user = await repo.get_by_email("nonexistent@example.com")

    assert user is None


@pytest.mark.asyncio(loop_scope="session")
async def test_get_nonexistent_user_by_id(db_session):
    """Test getting a nonexistent user by ID."""
    repo = UserRepository(db_session)

    user = await repo.get_by_id(999999)  # A user ID that doesn't exist

    assert user is None
