import logging

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import get_db
from app.main import app
from app.db.base import Base
from app.core.config import settings

# Import fixtures from feature-specific conftest files
pytest_plugins = [
    "app.tests.users.fixtures",
    "app.tests.posts.fixtures",
]

# Create a new engine for the default database
default_engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Create a new engine for the test database
test_engine = create_async_engine(settings.TEST_DATABASE_URL, echo=True)


@pytest_asyncio.fixture(scope="session")
async def test_db():
    # Create the test database if it does not exist
    async with default_engine.connect() as conn:
        try:
            await conn.execute(text("COMMIT"))
            await conn.execute(text("CREATE DATABASE test_db"))
        except ProgrammingError:
            logging.warning("Database already exists, continuing...")

    # Create tables in the test database
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Drop tables in the test database
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    # Drop the test database
    async with default_engine.connect() as conn:
        await conn.execute(text("COMMIT"))  # Ensure no transaction is active
        await conn.execute(text("""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = 'test_db'
              AND pid <> pg_backend_pid();
        """))
        await conn.execute(text("DROP DATABASE test_db"))


@pytest_asyncio.fixture(scope="session")
async def db_session(test_db):
    AsyncSessionLocal = sessionmaker(bind=test_engine, class_=AsyncSession,
                                     expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        yield session
    await session.close()


@pytest_asyncio.fixture(scope="session")
async def client(db_session):
    # Override the get_db dependency
    async def override_get_db():
        try:
            yield db_session
        finally:
            await db_session.close()

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://localhost:8000/"
    ) as ac:
        yield ac

    # Clean up override after tests
    app.dependency_overrides.clear()
