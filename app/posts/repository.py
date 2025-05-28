from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.posts.models import Post
from app.posts.schemas import PostCreate


class PostRepository:
    """
    Repository class for handling database operations related to posts
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, post: PostCreate, user_id: int) -> Post:
        """
        Create a new post in the database

        Args:
            post: Post data to create
            user_id: ID of the user who owns the post

        Returns:
            Post: Created post object
        """
        db_post = Post(
            text=post.text,
            user_id=user_id
        )
        self.db.add(db_post)
        await self.db.commit()
        await self.db.refresh(db_post)
        return db_post

    async def get_by_user_id(self, user_id: int) -> list[Post]:
        """
        Get all posts for a specific user

        Args:
            user_id: ID of the user

        Returns:
            list[Post]: List of user's posts
        """
        query = select(Post).filter(Post.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_id(self, post_id: int) -> Post | None:
        """
        Get a post by its ID

        Args:
            post_id: ID of the post

        Returns:
            Post | None: Post object if found, None otherwise
        """
        query = select(Post).filter(Post.id == post_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def delete(self, post_id: int, user_id: int) -> bool:
        """
        Delete a post by ID if it belongs to the specified user

        Args:
            post_id: ID of the post to delete
            user_id: ID of the user who owns the post

        Returns:
            bool: True if deleted, False if post not found
        """
        post = await self.get_by_id(post_id)
        if not post or post.user_id != user_id:
            return False

        query = delete(Post).filter(Post.id == post_id,
                                    Post.user_id == user_id)
        await self.db.execute(query)
        await self.db.commit()
        return True
