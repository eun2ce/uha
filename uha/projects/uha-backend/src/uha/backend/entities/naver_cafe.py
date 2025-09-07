"""Naver Cafe domain entities."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl


class NaverCafeProfile(BaseModel):
    """Naver Cafe profile entity."""

    id: UUID = Field(default_factory=uuid4, description="Internal profile identifier")
    cafe_id: str = Field(min_length=1, description="Naver Cafe ID")
    nickname: str = Field(min_length=1, max_length=50, description="User nickname")
    member_level: str = Field(description="Member level in cafe")
    visit_count: str = Field(description="Visit count")
    activity_score: str = Field(description="Activity score")
    profile_image_url: Optional[HttpUrl] = Field(None, description="Profile image URL")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class NaverCafeArticle(BaseModel):
    """Naver Cafe article entity."""

    id: UUID = Field(default_factory=uuid4, description="Internal article identifier")
    article_id: str = Field(min_length=1, description="Naver Cafe article ID")
    cafe_id: str = Field(min_length=1, description="Naver Cafe ID")
    title: str = Field(min_length=1, max_length=200, description="Article title")
    content: Optional[str] = Field(None, description="Article content")
    author: str = Field(min_length=1, description="Article author")
    date: str = Field(description="Article date")
    view_count: str = Field(description="View count")
    comment_count: str = Field(description="Comment count")
    link: str = Field(description="Article link")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    def get_view_count_int(self) -> int:
        """Convert view count string to integer."""
        try:
            return int(self.view_count.replace(",", ""))
        except (ValueError, AttributeError):
            return 0

    def get_comment_count_int(self) -> int:
        """Convert comment count string to integer."""
        try:
            return int(self.comment_count.replace(",", ""))
        except (ValueError, AttributeError):
            return 0
