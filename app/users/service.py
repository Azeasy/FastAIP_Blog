from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.users.schemas import UserCreate, UserRead
from app.users.repository import UserRepository
from app.core.security import verify_password


class UserService:
    """
    Service class for handling user-related business logic
    """
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def register(self, user: UserCreate) -> UserRead:
        """
        Register a new user

        Args:
            user: User data to register

        Returns:
            UserRead: Created user data

        Raises:
            HTTPException: If email is already registered
        """
        existing_user = await self.repo.get_by_email(user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        db_user = await self.repo.create(user)
        return UserRead.model_validate(db_user)

    async def authenticate(self, email: str, password: str) -> UserRead | None:
        """
        Authenticate a user with email and password

        Args:
            email: User's email address
            password: User's password

        Returns:
            UserRead | None: User data if auth succeeds, None otherwise
        """
        user = await self.repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return UserRead.model_validate(user)
