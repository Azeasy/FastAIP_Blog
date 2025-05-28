import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt

from app.core.security import (
    get_password_hash,
    verify_password,
    create_token,
    create_access_token,
    get_current_user,
)
from app.core.config import settings
from fastapi import HTTPException


def test_password_hashing():
    """Test password hashing and verification."""
    password = "testpassword123"
    hashed = get_password_hash(password)

    # Hashed password should be different from original
    assert hashed != password

    # Verification should work
    assert verify_password(password, hashed)

    # Wrong password should not verify
    assert not verify_password("wrongpassword", hashed)


def test_create_token():
    """Test token creation with custom claims."""
    data = {"sub": "user123", "role": "admin"}
    expires_delta = timedelta(minutes=15)

    token = create_token(data, expires_delta)

    # Decode and verify the token
    payload = jwt.decode(token, settings.SECRET_KEY,
                         algorithms=[settings.ALGORITHM])

    # Check if our claims are in the payload
    assert payload["sub"] == "user123"
    assert payload["role"] == "admin"

    # Check if expiration time is set
    assert "exp" in payload


def test_create_access_token():
    """Test access token creation."""
    user_id = "user123"

    token = create_access_token(user_id)

    # Decode and verify the token
    payload = jwt.decode(token, settings.SECRET_KEY,
                         algorithms=[settings.ALGORITHM])

    # Check if user_id is in the sub claim
    assert payload["sub"] == user_id

    # Check if expiration time is set
    assert "exp" in payload

    # Check that expiration is in the future
    exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    now = datetime.now(timezone.utc)
    assert exp_time > now


@pytest.mark.asyncio(loop_scope="session")
async def test_get_current_user_invalid_token(db_session):
    """Test getting the current user with an invalid token."""
    from fastapi.security.http import HTTPAuthorizationCredentials

    # Create credentials with an invalid token
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="invalid.token.here"
    )

    # Getting the current user should raise an exception
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(credentials, db_session)

    assert excinfo.value.status_code == 401
    assert "Could not validate credentials" in excinfo.value.detail
