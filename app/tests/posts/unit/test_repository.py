import pytest
from app.posts.repository import PostRepository
from app.posts.schemas import PostCreate


@pytest.mark.asyncio(loop_scope="session")
async def test_create_post(db_session, test_user):
    """Test creating a post via repository."""
    repo = PostRepository(db_session)
    post_data = PostCreate(text="Repository test post")

    created_post = await repo.create(post_data, test_user.id)

    assert created_post.id is not None
    assert created_post.text == "Repository test post"
    assert created_post.user_id == test_user.id


@pytest.mark.asyncio(loop_scope="session")
async def test_get_posts_by_user_id(db_session, test_user, test_posts):
    """Test getting posts by user ID."""
    repo = PostRepository(db_session)

    posts = await repo.get_by_user_id(test_user.id)

    assert len(posts) >= 3  # We should have at least 3 posts from the fixture
    for post in posts:
        assert post.user_id == test_user.id


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_post(db_session, test_user):
    """Test deleting a post."""
    # First create a post to delete
    repo = PostRepository(db_session)
    post_data = PostCreate(text="Post to delete")
    created_post = await repo.create(post_data, test_user.id)

    # Verify it exists
    post = await repo.get_by_id(created_post.id)
    assert post is not None

    # Delete it
    result = await repo.delete(created_post.id, test_user.id)
    assert result is True

    # Verify it's gone
    post = await repo.get_by_id(created_post.id)
    assert post is None


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_post_wrong_user(db_session, test_user):
    """Test that a post can't be deleted by the wrong user."""
    # Create a post
    repo = PostRepository(db_session)
    post_data = PostCreate(text="Post with wrong user")
    created_post = await repo.create(post_data, test_user.id)

    # Try to delete with a different user ID
    wrong_user_id = test_user.id + 999  # Guaranteed to be different
    result = await repo.delete(created_post.id, wrong_user_id)

    # Should not be able to delete
    assert result is False

    # Post should still exist
    post = await repo.get_by_id(created_post.id)
    assert post is not None
