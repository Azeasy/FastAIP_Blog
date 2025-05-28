from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.schemas import UserCreate, UserLogin, UserRead, Token
from app.users.service import UserService
from app.core.security import create_access_token
from app.db.session import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead,
             status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user

    Args:
        user: User data with email and password
        db: Database session

    Returns:
        UserRead: Created user data
    """
    service = UserService(db)
    try:
        new_user = await service.register(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(e))
    return new_user


@router.post("/login", response_model=Token)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Login with email and password

    Args:
        data: Login credentials with email and password
        db: Database session

    Returns:
        Token: JWT access token
    """
    service = UserService(db)
    user = await service.authenticate(data.email, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    access_token = create_access_token(sub=str(user.id))
    return {"access_token": access_token, "token_type": "bearer"}
