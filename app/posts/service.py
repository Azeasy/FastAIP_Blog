from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.posts.repository import PostRepository
from app.posts.schemas import PostCreate, PostRead
from app.core.cache import RedisCache


class PostService:
    """
    Service class for handling post-related business logic
    """
    def __init__(self, db: AsyncSession):
        self.repo = PostRepository(db)
        self.cache = RedisCache()

    async def create_post(self, post: PostCreate, user_id: int) -> PostRead:
        """
        Create a new post and clear user's post cache

        Args:
            post: Post data to create
            user_id: ID of the user creating the post

        Returns:
            PostRead: Created post data
        """
        # Validate payload size (limit to 1 MB)
        post_size = len(post.text.encode('utf-8'))
        if post_size > 1024 * 1024:  # 1 MB in bytes
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Post content exceeds the maximum size of 1 MB"
            )

        db_post = await self.repo.create(post, user_id)

        # Clear user's posts cache
        self.cache.clear_user_cache(user_id)

        return PostRead.model_validate(db_post)

    async def get_user_posts(self, user_id: int) -> list[PostRead]:
        """
        Get all posts for a user with caching

        Args:
            user_id: ID of the user

        Returns:
            list[PostRead]: List of user's posts
        """
        # Try to get from cache first
        cache_key = f"user:{user_id}:posts"
        cached_posts = self.cache.get(cache_key)

        if cached_posts:
            return [PostRead.model_validate(post) for post in cached_posts]

        # If not in cache, get from database
        posts = await self.repo.get_by_user_id(user_id)

        # Create serializable post data for caching
        # Only include the columns we need
        posts_data = [
            {
                "id": post.id,
                "text": post.text,
                "user_id": post.user_id
            }
            for post in posts
        ]

        # Cache the serialized data
        self.cache.set(cache_key, posts_data)

        return [PostRead.model_validate(post) for post in posts]

    async def delete_post(self, post_id: int, user_id: int) -> bool:
        """
        Delete a post and clear user's post cache

        Args:
            post_id: ID of the post to delete
            user_id: ID of the user who owns the post

        Returns:
            bool: True if deleted, False if post not found
        """
        result = await self.repo.delete(post_id, user_id)

        if result:
            # Clear user's posts cache
            self.cache.clear_user_cache(user_id)

        return result
