"""Stream data models."""

from typing import List, Optional

from pydantic import BaseModel


class LiveStreamEntry(BaseModel):
    """Basic live stream entry from markdown data."""

    date: str
    url: str


class StreamWithDetails(BaseModel):
    """Stream data with detailed information from YouTube API and AI analysis."""

    date: str
    url: str
    video_id: str
    title: Optional[str] = None
    thumbnail: Optional[str] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    duration: Optional[str] = None
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    # AI-generated content
    ai_summary: Optional[str] = None
    highlights: Optional[List[str]] = None
    sentiment: Optional[str] = None
    engagement_score: Optional[float] = None
    category: Optional[str] = None


class PaginatedStreamsRequest(BaseModel):
    """Request model for paginated streams."""

    year: int
    page: int = 1
    per_page: int = 10
    include_details: bool = False


class PaginatedStreamsResponse(BaseModel):
    """Response model for paginated streams."""

    streams: List[StreamWithDetails]
    total_streams: int
    current_page: int
    total_pages: int
    per_page: int
