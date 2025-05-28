from datetime import datetime, timedelta, timezone
import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db


class CustomHTTPBearer(HTTPBearer):
    """
    Custom HTTP Bearer that returns 401 Unauthorized instead of 403 Forbidden
    for missing or invalid tokens.
    """
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        try:
            return await super().__call__(request)
        except HTTPException as exc:
            # Change 403 Forbidden to 401 Unauthorized
            if exc.status_code == 403:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            raise exc


oauth2_scheme = CustomHTTPBearer()
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt

    Args:
        password: Plain text password

    Returns:
        str: Hashed password
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        bool: True if password matches, False otherwise
    """
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def create_token(data: dict, expires_delta: timedelta) -> str:
    """
    Create a JWT token

    Args:
        data: Data to encode in the token
        expires_delta: Time until token expiration

    Returns:
        str: JWT token
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY,
                      algorithm=settings.ALGORITHM)


def create_access_token(sub: str) -> str:
    """
    Create an access token

    Args:
        sub: Subject of the token (usually user ID)

    Returns:
        str: JWT access token
    """
    return create_token(
        {"sub": sub},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)):
    """
    Get the current authenticated user from token

    Args:
        credentials: HTTP authorization credentials
        db: Database session

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        token = credentials.credentials
        if not token:
            raise credentials_exception
        token = token.split(" ")[1] if " " in token else token
        payload = jwt.decode(token, settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    from app.users.repository import UserRepository
    user = await UserRepository(db).get_by_id(int(user_id))
    if not user:
        raise credentials_exception
    return user
