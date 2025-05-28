import pytest
from jose import jwt

from app.core.config import settings


@pytest.mark.asyncio(loop_scope="session")
async def test_register_user(client, db_session):
    """Test user registration endpoint."""
    response = await client.post(
        "/auth/register",
        json={"email": "test2@example.com", "password": "testpass123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test2@example.com"
    assert "id" in data
    assert "password" not in data  # Password should not be in response


@pytest.mark.asyncio(loop_scope="session")
async def test_register_duplicate_email(client):
    """Test registering with a duplicate email."""
    # First register a user
    email = "duplicate@example.com"
    await client.post(
        "/auth/register",
        json={"email": email, "password": "testpass123"}
    )

    # Try to register again with the same email
    response = await client.post(
        "/auth/register",
        json={"email": email, "password": "anotherpass"}
    )

    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


@pytest.mark.asyncio(loop_scope="session")
async def test_login_user(client):
    """Test user login endpoint."""
    # First register a user
    email = "test1@example.com"
    password = "testpass123"
    await client.post(
        "/auth/register",
        json={"email": email, "password": password}
    )

    # Then try to login
    response = await client.post(
        "/auth/login",
        json={"email": email, "password": password}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

    # Validate JWT token
    token = data["access_token"]
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )
    assert "sub" in payload  # Subject (user ID)
    assert "exp" in payload  # Expiration time


@pytest.mark.asyncio(loop_scope="session")
async def test_login_wrong_password(client):
    """Test login with wrong password."""
    # First register a user
    email = "test3@example.com"
    password = "testpass123"
    await client.post(
        "/auth/register",
        json={"email": email, "password": password}
    )

    # Try to login with wrong password
    response = await client.post(
        "/auth/login",
        json={"email": email, "password": "wrongpass"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio(loop_scope="session")
async def test_login_nonexistent_user(client):
    """Test login with nonexistent user email."""
    response = await client.post(
        "/auth/login",
        json={"email": "nonexistent@example.com", "password": "anypassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio(loop_scope="session")
async def test_protected_endpoint_without_token(client):
    """Test accessing a protected endpoint without a token."""
    response = await client.get("/posts/")

    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]
