from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.posts.schemas import PostCreate, PostRead
from app.posts.service import PostService
from app.core.security import get_current_user
from app.users.models import User
from app.db.session import get_db

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/", response_model=PostRead, status_code=status.HTTP_201_CREATED)
async def add_post(
    post: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new post

    Args:
        post: Post data to create
        db: Database session
        current_user: Authenticated user

    Returns:
        PostRead: Created post data
    """
    service = PostService(db)
    return await service.create_post(post, current_user.id)


@router.get("/", response_model=List[PostRead])
async def get_posts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all posts for the authenticated user

    Args:
        db: Database session
        current_user: Authenticated user

    Returns:
        List[PostRead]: List of user's posts
    """
    service = PostService(db)
    return await service.get_user_posts(current_user.id)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a post

    Args:
        post_id: ID of the post to delete
        db: Database session
        current_user: Authenticated user

    Returns:
        None
    """
    service = PostService(db)
    result = await service.delete_post(post_id, current_user.id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with ID {post_id} not found"
        )
