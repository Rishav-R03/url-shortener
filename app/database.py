# app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from datetime import datetime
import asyncio
from config import settings

# Base class for declarative models
Base = declarative_base()

class URL(Base):
    """
    SQLAlchemy model for storing original and short URLs.
    """
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String, unique=True, index=True, nullable=False)
    long_url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    # user_id can be added here if authentication is implemented

class ClickEvent(Base):
    """
    SQLAlchemy model for storing click events for short URLs.
    """
    __tablename__ = "click_events"

    id = Column(Integer, primary_key=True, index=True)
    short_code_id = Column(Integer, ForeignKey("urls.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String, nullable=True) # Store IP for basic analytics

# Create an async engine
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Create a sessionmaker for async sessions
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

async def init_db():
    """
    Initializes the database by creating all tables.
    Includes a retry mechanism to handle database startup delays.
    """
    MAX_RETRIES = 10
    RETRY_DELAY_SECONDS = 5 # Wait 5 seconds between retries

    for i in range(MAX_RETRIES):
        try:
            print(f"Attempting to connect to database and create tables (Attempt {i+1}/{MAX_RETRIES})...")
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("Database tables created successfully.")
            return # Exit function if successful
        except Exception as e:
            print(f"Database connection failed: {e}")
            if i < MAX_RETRIES - 1:
                print(f"Retrying in {RETRY_DELAY_SECONDS} seconds...")
                await asyncio.sleep(RETRY_DELAY_SECONDS)
            else:
                print("Max retries reached. Could not connect to database.")
                raise # Re-raise the last exception if all retries fail

async def get_db():
    """
    Dependency for FastAPI to get an async database session.
    Ensures the session is closed after the request.
    """
    async with AsyncSessionLocal() as session:
        yield session

