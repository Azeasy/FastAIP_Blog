from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserBase(BaseModel):
    """
    Base schema for user data
    """
    email: EmailStr = Field(..., description="User email address")


class UserCreate(UserBase):
    """
    Schema for creating a new user
    """
    password: str = Field(..., min_length=8, description="User password")


class UserLogin(UserBase):
    """
    Schema for user login
    """
    password: str = Field(..., description="User password")


class UserRead(UserBase):
    """
    Schema for reading user data
    """
    id: int = Field(..., description="User ID")

    model_config = ConfigDict(
        from_attributes=True,
    )


class Token(BaseModel):
    """
    Schema for authentication token
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
