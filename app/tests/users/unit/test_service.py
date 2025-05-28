import pytest
from fastapi import HTTPException

from app.users.service import UserService
from app.users.schemas import UserCreate


@pytest.mark.asyncio(loop_scope="session")
async def test_register_user_service(db_session):
    """Test registering a user via service."""
    service = UserService(db_session)
    user_data = UserCreate(email="serviceuser@example.com",
                           password="servicepass123")

    created_user = await service.register(user_data)

    assert created_user.id is not None
    assert created_user.email == "serviceuser@example.com"


@pytest.mark.asyncio(loop_scope="session")
async def test_authenticate_user_success(db_session):
    """Test successful user authentication."""
    # First register a user
    service = UserService(db_session)
    email = "auth_test@example.com"
    password = "authpass123"

    user_data = UserCreate(email=email, password=password)
    await service.register(user_data)

    # Now try to authenticate
    authenticated_user = await service.authenticate(email, password)

    assert authenticated_user is not None
    assert authenticated_user.email == email


@pytest.mark.asyncio(loop_scope="session")
async def test_authenticate_nonexistent_user(db_session):
    """Test authenticating a nonexistent user."""
    service = UserService(db_session)

    authenticated_user = await service.authenticate("nonexistent@example.com",
                                                    "wrongpass")

    assert authenticated_user is None


@pytest.mark.asyncio(loop_scope="session")
async def test_authenticate_wrong_password(db_session):
    """Test authenticating with wrong password."""
    # First register a user
    service = UserService(db_session)
    email = "wrong_pass@example.com"
    password = "correctpass123"

    user_data = UserCreate(email=email, password=password)
    await service.register(user_data)

    # Now try to authenticate with wrong password
    authenticated_user = await service.authenticate(email, "wrongpass123")

    assert authenticated_user is None
