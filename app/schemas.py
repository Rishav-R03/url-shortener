# app/schemas.py
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional

class URLCreate(BaseModel):
    """
    Pydantic model for creating a new short URL.
    long_url uses HttpUrl for validation.
    """
    long_url: HttpUrl

class URLResponse(BaseModel):
    """
    Pydantic model for the response when a URL is shortened.
    """
    short_code: str
    long_url: str
    created_at: datetime
    id: int

    class Config:
        from_attributes = True # Allows mapping from SQLAlchemy models

class ClickEventResponse(BaseModel):
    """
    Pydantic model for a single click event.
    """
    timestamp: datetime
    ip_address: Optional[str] = None # IP address might not always be captured

    class Config:
        from_attributes = True

class URLAnalytics(BaseModel):
    """
    Pydantic model for URL analytics, including total clicks.
    """
    short_code: str
    long_url: str
    created_at: datetime
    total_clicks: int

    class Config:
        from_attributes = True

