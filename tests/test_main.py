# tests/test_main.py
import pytest
from httpx import AsyncClient
from app.config import settings
from app.main import request_timestamps # Import for clearing in tests

@pytest.mark.asyncio
async def test_read_root(client: AsyncClient):
    """
    Test the root endpoint.
    """
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the URL Shortener API! Use /docs for API documentation."}

@pytest.mark.asyncio
async def test_create_short_url(client: AsyncClient):
    """
    Test successful URL shortening.
    """
    long_url = "https://example.com/very/long/url/for/testing"
    response = await client.post("/shorten", json={"long_url": long_url})

    assert response.status_code == 201
    data = response.json()
    assert "short_code" in data
    assert len(data["short_code"]) == settings.SHORT_CODE_LENGTH
    assert data["long_url"] == long_url
    assert "created_at" in data
    assert "id" in data

    # Verify it's in the database (optional, but good for integration test)
    # You could add a direct DB query here using db_session fixture if needed
    # For now, we'll rely on redirection test to confirm persistence.

@pytest.mark.asyncio
async def test_create_short_url_invalid_input(client: AsyncClient):
    """
    Test URL shortening with invalid URL input.
    """
    response = await client.post("/shorten", json={"long_url": "not-a-valid-url"})
    assert response.status_code == 422 # Unprocessable Entity for Pydantic validation error

@pytest.mark.asyncio
async def test_redirect_short_url(client: AsyncClient):
    """
    Test successful redirection and click recording.
    """
    long_url = "https://www.test-redirect.com"
    shorten_response = await client.post("/shorten", json={"long_url": long_url})
    short_code = shorten_response.json()["short_code"]

    redirect_response = await client.get(f"/{short_code}", follow_redirects=False)
    assert redirect_response.status_code == 307 # Temporary Redirect
    assert redirect_response.headers["location"] == long_url

    # Verify click count
    analytics_response = await client.get(f"/analytics/{short_code}")
    assert analytics_response.status_code == 200
    assert analytics_response.json()["total_clicks"] == 1

    # Test another click
    await client.get(f"/{short_code}", follow_redirects=False)
    analytics_response_after_second_click = await client.get(f"/analytics/{short_code}")
    assert analytics_response_after_second_click.status_code == 200
    assert analytics_response_after_second_click.json()["total_clicks"] == 2


@pytest.mark.asyncio
async def test_redirect_non_existent_short_url(client: AsyncClient):
    """
    Test redirection for a short URL that does not exist.
    """
    response = await client.get("/nonexistentcode", follow_redirects=False)
    assert response.status_code == 404
    assert response.json()["detail"] == "Short URL not found"

@pytest.mark.asyncio
async def test_get_url_analytics(client: AsyncClient):
    """
    Test retrieving analytics for an existing short URL.
    """
    long_url = "https://analytics.test.com"
    shorten_response = await client.post("/shorten", json={"long_url": long_url})
    short_code = shorten_response.json()["short_code"]

    # Simulate a few clicks
    await client.get(f"/{short_code}", follow_redirects=False)
    await client.get(f"/{short_code}", follow_redirects=False)

    response = await client.get(f"/analytics/{short_code}")
    assert response.status_code == 200
    data = response.json()
    assert data["short_code"] == short_code
    assert data["long_url"] == long_url
    assert data["total_clicks"] == 2
    assert "created_at" in data

@pytest.mark.asyncio
async def test_get_url_analytics_non_existent(client: AsyncClient):
    """
    Test retrieving analytics for a non-existent short URL.
    """
    response = await client.get("/analytics/nonexistentanalytics")
    assert response.status_code == 404
    assert response.json()["detail"] == "Short URL not found or no analytics available"

@pytest.mark.asyncio
async def test_rate_limiting(client: AsyncClient):
    """
    Test the rate limiting functionality for URL creation.
    """
    # Clear any previous rate limit data for this test's client IP
    request_timestamps.clear()

    long_url_base = "https://rate.limit.test.com/"

    # Make requests up to the limit
    for i in range(settings.RATE_LIMIT_PER_MINUTE):
        response = await client.post("/shorten", json={"long_url": f"{long_url_base}{i}"})
        assert response.status_code == 201, f"Request {i+1} failed unexpectedly: {response.json()}"

    # The next request should be rate-limited
    response = await client.post("/shorten", json={"long_url": f"{long_url_base}overlimit"})
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["detail"]

    # Wait for more than 60 seconds and try again
    # In a real test, you'd use time.sleep(61)
    # For pytest, we can mock time or rely on the fixture clearing for isolation.
    # Since conftest.py clears request_timestamps for each test,
    # a new call to client.post will essentially reset the rate limit for this test.
    # To properly test waiting, you'd need to mock time or run this in a separate test
    # with actual sleep, which is slow for unit tests.
    # For this test, we've verified the 429 response.
