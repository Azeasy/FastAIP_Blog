from pydantic import BaseModel, Field, ConfigDict


class PostBase(BaseModel):
    text: str = Field(..., description="Post content text")


class PostCreate(PostBase):
    """
    Schema for creating a new post
    """
    pass


class PostRead(PostBase):
    """
    Schema for reading post data
    """
    id: int
    user_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )


class PostDelete(BaseModel):
    """
    Schema for deleting a post
    """
    post_id: int = Field(..., description="ID of the post to delete")
