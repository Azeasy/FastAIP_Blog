from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.users.models import User
from app.users.schemas import UserCreate
from app.core.security import get_password_hash


class UserRepository:
    """
    Repository class for handling database operations related to users
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        """
        Get a user by email

        Args:
            email: User's email address

        Returns:
            User | None: User object if found, None otherwise
        """
        query = select(User).filter(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        """
        Get a user by ID

        Args:
            user_id: User's ID

        Returns:
            User | None: User object if found, None otherwise
        """
        query = select(User).filter(User.id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(self, user: UserCreate) -> User:
        """
        Create a new user

        Args:
            user: User data to create

        Returns:
            User: Created user object
        """
        db_user = User(
            email=user.email,
            hashed_password=get_password_hash(user.password)
        )
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user
