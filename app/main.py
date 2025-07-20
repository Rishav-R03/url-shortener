# app/main.py
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from database import init_db, get_db
from redis_client import get_redis_client, close_redis_connection
from schemas import URLCreate, URLResponse, URLAnalytics
from config import settings
import crud 
from collections import defaultdict
import time

app = FastAPI(
    title="URL Shortener",
    description="A simple URL shortener with analytics and caching using FastAPI, PostgreSQL, and Redis.",
    version="1.0.0"
)

# In-memory dictionary for basic rate limiting
# Key: IP address, Value: List of timestamps for requests
request_timestamps = defaultdict(list)

@app.on_event("startup")
async def startup_event():
    """
    Handles startup events: initializes the database.
    """
    print("Starting up application...")
    await init_db()
    print("Database initialized.")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Handles shutdown events: closes Redis connection.
    """
    print("Shutting down application...")
    await close_redis_connection()
    print("Redis connection closed.")

def get_client_ip(request: Request) -> str:
    """
    Extracts the client's IP address from the request.
    Considers X-Forwarded-For header if present (e.g., when behind a proxy).
    """
    if "x-forwarded-for" in request.headers:
        return request.headers["x-forwarded-for"].split(",")[0].strip()
    return request.client.host

async def rate_limit_dependency(request: Request):
    """
    FastAPI dependency for rate limiting URL creation requests.
    Limits requests based on IP address.
    """
    ip_address = get_client_ip(request)
    current_time = time.time()

    # Remove timestamps older than 1 minute
    request_timestamps[ip_address] = [
        t for t in request_timestamps[ip_address] if current_time - t < 60
    ]

    if len(request_timestamps[ip_address]) >= settings.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Please try again in {60 - (current_time - request_timestamps[ip_address][0]):.0f} seconds."
        )
    request_timestamps[ip_address].append(current_time)

@app.post("/shorten", response_model=URLResponse, status_code=status.HTTP_201_CREATED)
async def create_short_url_endpoint(
    url: URLCreate,
    db: AsyncSession = Depends(get_db),
    redis_client: Redis = Depends(get_redis_client),
    # Apply rate limiting to this endpoint
    rate_limit: None = Depends(rate_limit_dependency)
):
    """
    Creates a new short URL for the given long URL.
    Returns the generated short code and other URL details.
    """
    db_url = await crud.create_short_url(db, url, redis_client)
    return db_url

@app.get("/{short_code}", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def redirect_to_long_url(
    short_code: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    redis_client: Redis = Depends(get_redis_client)
):
    """
    Redirects from the short URL to the original long URL.
    Records a click event for analytics.
    """
    long_url = await crud.get_long_url(db, short_code, redis_client)
    if not long_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found")

    # Record the click event asynchronously
    ip_address = get_client_ip(request)
    await crud.record_click(db, short_code, ip_address, redis_client)

    return RedirectResponse(url=long_url)

@app.get("/analytics/{short_code}", response_model=URLAnalytics)
async def get_url_analytics_endpoint(
    short_code: str,
    db: AsyncSession = Depends(get_db),
    redis_client: Redis = Depends(get_redis_client)
):
    """
    Retrieves analytics for a specific short URL, including total clicks.
    """
    analytics_data = await crud.get_url_analytics(db, short_code, redis_client)
    if not analytics_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short URL not found or no analytics available")
    return URLAnalytics(**analytics_data)

@app.get("/")
async def read_root():
    """
    Root endpoint for the API.
    """
    return {"message": "Welcome to the URL Shortener API! Use /docs for API documentation."}

