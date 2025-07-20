# app/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import URL, ClickEvent
from schemas import URLCreate
from utils import generate_short_code
from redis.asyncio import Redis
from config import settings

async def create_short_url(db: AsyncSession, url: URLCreate, redis_client: Redis) -> URL:
    """
    Creates a new short URL entry in the database and caches it in Redis.
    Generates a unique short code.
    """
    while True:
        short_code = generate_short_code()
        # Check if the short code already exists in the database
        existing_url = await db.scalar(select(URL).filter(URL.short_code == short_code))
        if not existing_url:
            break # Found a unique short code

    db_url = URL(long_url=str(url.long_url), short_code=short_code)
    db.add(db_url)
    await db.commit()
    await db.refresh(db_url)

    # Cache the short_code to long_url mapping in Redis
    # Set an expiration for the cache entry (e.g., 24 hours)
    await redis_client.setex(f"short:{short_code}", 86400, str(url.long_url))

    return db_url

async def get_long_url(db: AsyncSession, short_code: str, redis_client: Redis) -> str | None:
    """
    Retrieves the original long URL given a short code.
    Prioritizes fetching from Redis cache. If not found, fetches from DB and caches.
    """
    # Try to get from Redis cache first
    long_url = await redis_client.get(f"short:{short_code}")
    if long_url:
        return long_url

    # If not in cache, fetch from database
    db_url = await db.scalar(select(URL).filter(URL.short_code == short_code))
    if db_url:
        # Cache the result in Redis for future requests
        await redis_client.setex(f"short:{short_code}", 86400, db_url.long_url)
        return db_url.long_url
    return None

async def record_click(db: AsyncSession, short_code: str, ip_address: str | None, redis_client: Redis):
    """
    Records a click event for a short URL in the database and increments Redis counter.
    """
    db_url = await db.scalar(select(URL).filter(URL.short_code == short_code))
    if db_url:
        click_event = ClickEvent(short_code_id=db_url.id, ip_address=ip_address)
        db.add(click_event)
        await db.commit()

        # Increment click counter in Redis
        await redis_client.incr(f"clicks:{short_code}")
    else:
        # Handle case where short code doesn't exist (e.g., log an error)
        print(f"Warning: Attempted to record click for non-existent short code: {short_code}")


async def get_url_analytics(db: AsyncSession, short_code: str, redis_client: Redis) -> dict | None:
    """
    Retrieves analytics for a given short URL, including total clicks.
    Fetches total clicks from Redis, and URL details from the database.
    """
    db_url = await db.scalar(select(URL).filter(URL.short_code == short_code))
    if db_url:
        # Get total clicks from Redis
        total_clicks = await redis_client.get(f"clicks:{short_code}")
        if total_clicks is None:
            # If Redis counter is not present, aggregate from DB (initial sync or Redis restart)
            db_clicks = await db.scalar(
                select(func.count(ClickEvent.id)).filter(ClickEvent.short_code_id == db_url.id)
            )
            total_clicks = db_clicks if db_clicks is not None else 0
            # Optionally, set this value back to Redis for future consistency
            await redis_client.set(f"clicks:{short_code}", total_clicks)
        else:
            total_clicks = int(total_clicks)

        return {
            "short_code": db_url.short_code,
            "long_url": db_url.long_url,
            "created_at": db_url.created_at,
            "total_clicks": total_clicks
        }
    return None

