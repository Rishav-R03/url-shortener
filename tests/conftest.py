# tests/conftest.py
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db, engine as app_engine
from app.redis_client import get_redis_client, redis_client as app_redis_client
from app.config import settings
from app.main import request_timestamps # Import the rate limiting dictionary

# Use a separate test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:root123@localhost:5433/test_url_shortener_db"

# Create a test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestAsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
    class_=AsyncSession
)

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    """
    Sets up the test database: creates all tables before tests run
    and drops them after all tests are finished.
    """
    print("\nSetting up test database...")
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    print("Tearing down test database...")
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session():
    """
    Provides an isolated database session for each test.
    Rolls back changes after each test to ensure a clean state.
    """
    async with TestAsyncSessionLocal() as session:
        # Begin a transaction
        await session.begin()
        try:
            yield session
        finally:
            # Rollback the transaction to clean up changes
            await session.rollback()
            await session.close()

@pytest_asyncio.fixture
async def test_redis_client():
    """
    Provides a Redis client for tests and flushes the test Redis DB
    before each test to ensure a clean state.
    """
    # Connect to a separate Redis DB for testing if possible, or flush the default
    # For simplicity, we'll use the same host/port but ensure it's flushed.
    test_redis = app_redis_client # Re-use the app's client for simplicity, but ensure isolation
    await test_redis.flushdb() # Clear all keys from the current DB
    yield test_redis
    await test_redis.flushdb() # Clear again after test

@pytest_asyncio.fixture
async def client(db_session: AsyncSession, test_redis_client):
    """
    Provides an asynchronous test client for FastAPI,
    overriding database and Redis dependencies.
    """
    def override_get_db():
        yield db_session

    def override_get_redis_client():
        yield test_redis_client

    # Override the dependencies in the FastAPI app
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis_client] = override_get_redis_client

    # Clear the rate limiting timestamps for each test
    request_timestamps.clear()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    # Clean up overrides after the test
    app.dependency_overrides.clear()

