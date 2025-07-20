# app/redis_client.py
import redis.asyncio as redis
from config import settings

# Initialize an asynchronous Redis client
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True # Decodes responses to Python strings
)

async def get_redis_client():
    """
    Dependency for FastAPI to get an async Redis client.
    """
    yield redis_client

async def close_redis_connection():
    """
    Closes the Redis connection.
    Should be called on application shutdown.
    """
    await redis_client.close()

