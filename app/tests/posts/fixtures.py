import pytest_asyncio

from app.posts.models import Post


@pytest_asyncio.fixture(scope="session")
async def test_post(db_session, test_user):
    """Create a test post fixture."""
    post = Post(text="Test post content", user_id=test_user.id)
    db_session.add(post)
    await db_session.commit()
    await db_session.refresh(post)
    return post


@pytest_asyncio.fixture(scope="session")
async def test_posts(db_session, test_user):
    """Create multiple test posts for a user."""
    posts = []
    for i in range(3):
        post = Post(text=f"Test post content {i}", user_id=test_user.id)
        db_session.add(post)
        posts.append(post)

    await db_session.commit()

    # Refresh all posts to get their IDs
    for post in posts:
        await db_session.refresh(post)

    return posts
