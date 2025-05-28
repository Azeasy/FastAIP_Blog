import pytest


@pytest.mark.asyncio(loop_scope="session")
async def test_create_post(client, test_user_token):
    """Test creating a new post."""
    # Create a post
    response = await client.post(
        "/posts/",
        json={"text": "This is a test post"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "This is a test post"
    assert "id" in data
    assert "user_id" in data


@pytest.mark.asyncio(loop_scope="session")
async def test_get_posts(client, test_user_token, test_posts):
    """Test getting all posts for the authenticated user."""
    response = await client.get(
        "/posts/",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3

    # Check structure of returned posts
    for post in data:
        assert "id" in post
        assert "text" in post
        assert "user_id" in post


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_nonexistent_post(client, test_user_token):
    """Test deleting a post that doesn't exist."""
    response = await client.delete(
        "/posts/99999",  # A post ID that doesn't exist
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@pytest.mark.asyncio(loop_scope="session")
async def test_unauthorized_access(client):
    """Test accessing endpoints without authentication."""
    # Try to get posts without token
    response = await client.get("/posts/")
    assert response.status_code == 401

    # Try to create a post without token
    response = await client.post(
        "/posts/",
        json={"text": "Unauthorized post"}
    )
    assert response.status_code == 401

    # Try to delete a post without token
    response = await client.delete("/posts/1")
    assert response.status_code == 401


@pytest.mark.asyncio(loop_scope="session")
async def test_large_post_creation(client, test_user_token):
    """Test creating a post that exceeds size limit."""
    # Create a post with content larger than 1MB (1MB = 1048576 bytes)
    large_text = "x" * 1048577  # Just over 1MB

    response = await client.post(
        "/posts/",
        json={"text": large_text},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 413  # Request Entity Too Large
    assert "exceeds" in response.json()["detail"]
