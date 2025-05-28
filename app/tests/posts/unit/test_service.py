import pytest
from fastapi import HTTPException
from unittest.mock import patch

from app.posts.service import PostService
from app.posts.schemas import PostCreate
from app.core.cache import RedisCache


@pytest.mark.asyncio(loop_scope="session")
async def test_create_post_service(db_session, test_user):
    """Test creating a post via service."""
    service = PostService(db_session)
    post_data = PostCreate(text="Service test post")

    created_post = await service.create_post(post_data, test_user.id)

    assert created_post.id is not None
    assert created_post.text == "Service test post"
    assert created_post.user_id == test_user.id


@pytest.mark.asyncio(loop_scope="session")
async def test_create_post_too_large(db_session, test_user):
    """Test that creating a post with too much content fails."""
    service = PostService(db_session)
    # Create a post with content larger than 1MB (1MB = 1048576 bytes)
    large_text = "x" * 1048577  # Just over 1MB
    post_data = PostCreate(text=large_text)

    with pytest.raises(HTTPException) as excinfo:
        await service.create_post(post_data, test_user.id)

    assert excinfo.value.status_code == 413
    assert "exceeds" in excinfo.value.detail


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_posts_service(db_session, test_user, test_posts):
    """Test getting user posts via service."""
    service = PostService(db_session)

    # Clear cache first to ensure we're testing the database fetch
    cache = RedisCache()
    cache.clear_user_cache(test_user.id)

    posts = await service.get_user_posts(test_user.id)

    assert len(posts) >= 3  # At least 3 from the fixture
    for post in posts:
        assert post.user_id == test_user.id


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_posts_cached(db_session, test_user):
    """Test that posts are cached when fetched."""
    service = PostService(db_session)

    # Clear cache first
    cache = RedisCache()
    cache.clear_user_cache(test_user.id)

    # Mock the cache.get and cache.set methods
    with patch.object(RedisCache, 'get', return_value=None) as mock_get, \
         patch.object(RedisCache, 'set') as mock_set:

        # First call should miss cache and set it
        await service.get_user_posts(test_user.id)

        # Verify cache interactions
        mock_get.assert_called_once()
        mock_set.assert_called_once()


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_post_service(db_session, test_user):
    """Test deleting a post via service."""
    # First create a post to delete
    service = PostService(db_session)
    post_data = PostCreate(text="Service post to delete")
    created_post = await service.create_post(post_data, test_user.id)

    # Delete it
    result = await service.delete_post(created_post.id, test_user.id)
    assert result is True

    # Try to get the posts - deleted post should not be included
    posts = await service.get_user_posts(test_user.id)
    assert not any(post.id == created_post.id for post in posts)


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_nonexistent_post_service(db_session, test_user):
    """Test deleting a post that doesn't exist."""
    service = PostService(db_session)

    # Try to delete a post with a non-existent ID
    result = await service.delete_post(99999, test_user.id)
    assert result is False


@pytest.mark.asyncio(loop_scope="session")
async def test_cache_cleared_on_post_creation(db_session, test_user):
    """Test that cache is cleared when a post is created."""
    service = PostService(db_session)

    # Mock the cache.clear_user_cache method
    with patch.object(RedisCache, 'clear_user_cache') as mock_clear:
        post_data = PostCreate(text="Cache test post")
        await service.create_post(post_data, test_user.id)

        # Verify cache was cleared for the user
        mock_clear.assert_called_once_with(test_user.id)
