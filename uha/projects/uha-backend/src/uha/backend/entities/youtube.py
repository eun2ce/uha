"""YouTube domain entities."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl


class YouTubeChannel(BaseModel):
    """YouTube channel entity."""

    id: UUID = Field(default_factory=uuid4, description="Internal channel identifier")
    channel_id: str = Field(min_length=1, description="YouTube channel ID")
    title: str = Field(min_length=1, max_length=100, description="Channel title")
    description: Optional[str] = Field(None, max_length=5000, description="Channel description")
    custom_url: Optional[str] = Field(None, description="Channel custom URL")
    subscriber_count: Optional[int] = Field(None, ge=0, description="Subscriber count")
    video_count: Optional[int] = Field(None, ge=0, description="Total video count")
    view_count: Optional[int] = Field(None, ge=0, description="Total view count")
    thumbnail_url: Optional[HttpUrl] = Field(None, description="Channel thumbnail URL")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class YouTubeVideoStatistics(BaseModel):
    """YouTube video statistics value object."""

    view_count: int = Field(ge=0, description="View count")
    like_count: int = Field(ge=0, description="Like count")
    comment_count: int = Field(ge=0, description="Comment count")
    favorite_count: int = Field(ge=0, description="Favorite count")


class YouTubeVideoSnippet(BaseModel):
    """YouTube video snippet value object."""

    title: str = Field(min_length=1, max_length=100, description="Video title")
    description: Optional[str] = Field(None, max_length=5000, description="Video description")
    published_at: datetime = Field(description="Video publish date")
    channel_id: str = Field(min_length=1, description="Channel ID")
    channel_title: str = Field(min_length=1, description="Channel title")
    tags: List[str] = Field(default_factory=list, description="Video tags")
    category_id: Optional[str] = Field(None, description="YouTube category ID")
    default_language: Optional[str] = Field(None, description="Default language")
    thumbnails: Dict[str, Dict[str, str]] = Field(default_factory=dict, description="Thumbnail URLs")


class YouTubeVideoContentDetails(BaseModel):
    """YouTube video content details value object."""

    duration: str = Field(description="Video duration in ISO 8601 format")
    dimension: Optional[str] = Field(None, description="Video dimension (2d/3d)")
    definition: Optional[str] = Field(None, description="Video definition (hd/sd)")
    caption: Optional[str] = Field(None, description="Caption availability")
    licensed_content: Optional[bool] = Field(None, description="Licensed content flag")
    projection: Optional[str] = Field(None, description="Video projection")


class YouTubeComment(BaseModel):
    """YouTube comment entity."""

    id: str = Field(description="Comment ID")
    author_display_name: str = Field(description="Comment author name")
    author_profile_image_url: Optional[HttpUrl] = Field(None, description="Author profile image")
    text_display: str = Field(description="Comment text")
    like_count: int = Field(ge=0, description="Comment like count")
    published_at: datetime = Field(description="Comment publish date")
    updated_at: Optional[datetime] = Field(None, description="Comment update date")


class YouTubeVideo(BaseModel):
    """YouTube video aggregate root."""

    # Identity
    id: UUID = Field(default_factory=uuid4, description="Internal video identifier")
    video_id: str = Field(min_length=1, description="YouTube video ID")

    # Video Information
    snippet: YouTubeVideoSnippet = Field(description="Video snippet data")
    statistics: YouTubeVideoStatistics = Field(description="Video statistics")
    content_details: YouTubeVideoContentDetails = Field(description="Video content details")

    # Comments
    comments: List[YouTubeComment] = Field(default_factory=list, description="Video comments")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    def add_comment(self, comment: YouTubeComment) -> None:
        """Add a comment to the video."""
        self.comments.append(comment)
        self.updated_at = datetime.utcnow()

    def add_comments(self, comments: List[YouTubeComment]) -> None:
        """Add multiple comments to the video."""
        self.comments.extend(comments)
        self.updated_at = datetime.utcnow()

    def get_thumbnail_url(self, quality: str = "high") -> Optional[str]:
        """Get thumbnail URL by quality."""
        thumbnails = self.snippet.thumbnails
        if quality in thumbnails:
            return thumbnails[quality].get("url")

        # Fallback to available qualities
        for fallback_quality in ["maxres", "high", "medium", "default"]:
            if fallback_quality in thumbnails:
                return thumbnails[fallback_quality].get("url")

        return None

    def get_duration_minutes(self) -> int:
        """Parse ISO 8601 duration to minutes."""
        import re

        duration = self.content_details.duration
        match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration)
        if not match:
            return 0

        hours = int(match.group(1)) if match.group(1) else 0
        minutes = int(match.group(2)) if match.group(2) else 0
        seconds = int(match.group(3)) if match.group(3) else 0

        return hours * 60 + minutes + (seconds // 60)

    def get_top_comments(self, limit: int = 10) -> List[YouTubeComment]:
        """Get top comments sorted by like count."""
        return sorted(self.comments, key=lambda c: c.like_count, reverse=True)[:limit]
