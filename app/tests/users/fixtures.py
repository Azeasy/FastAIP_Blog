import pytest_asyncio
from datetime import datetime, timedelta, timezone
from jose import jwt

from app.core.config import settings
from app.users.models import User
from app.core.security import get_password_hash


@pytest_asyncio.fixture(scope="session")
async def test_user(db_session):
    """Fixture that creates a test user in the database."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword")
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="session")
async def test_user_token(test_user):
    """Fixture that creates a valid JWT token for the test user."""
    expire = (
        datetime.now(timezone.utc) +
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode = {"exp": expire, "sub": str(test_user.id)}
    return jwt.encode(to_encode, settings.SECRET_KEY,
                      algorithm=settings.ALGORITHM)


@pytest_asyncio.fixture(scope="session")
async def expired_token(test_user):
    """Fixture that creates an expired JWT token for the test user."""
    # Create a token that is expired 1 hour ago
    expire = datetime.now(timezone.utc) - timedelta(hours=1)
    to_encode = {"exp": expire, "sub": str(test_user.id)}
    return jwt.encode(to_encode, settings.SECRET_KEY,
                      algorithm=settings.ALGORITHM)
