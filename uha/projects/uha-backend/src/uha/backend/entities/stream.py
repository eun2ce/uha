"""Stream domain entities."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class StreamCategory(str, Enum):
    """Stream category enumeration."""

    GAMING = "🎮 게임"
    MUSIC = "🎵 음악"
    TALK = "🗣️ 토크"
    ART = "🎨 창작"
    EDUCATION = "📚 교육"
    COOKING = "🍳 요리"
    FITNESS = "🏃 운동"
    REVIEW = "🎬 리뷰"
    GENERAL = "📺 일반"


class StreamStatus(str, Enum):
    """Stream status enumeration."""

    SCHEDULED = "scheduled"
    LIVE = "live"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class StreamMetrics(BaseModel):
    """Stream metrics value object."""

    view_count: int = Field(ge=0, description="Total view count")
    like_count: int = Field(ge=0, description="Total like count")
    comment_count: int = Field(ge=0, description="Total comment count")
    duration_minutes: int = Field(ge=0, description="Stream duration in minutes")
    engagement_score: Decimal = Field(ge=0, le=10, description="Engagement score out of 10")

    @validator("engagement_score")
    def validate_engagement_score(cls, v):
        """Validate engagement score is within valid range."""
        return round(v, 2)


class StreamAnalysis(BaseModel):
    """Stream analysis value object."""

    ai_summary: str = Field(min_length=1, max_length=1000, description="AI-generated summary")
    highlights: List[str] = Field(default_factory=list, description="Stream highlights")
    sentiment: str = Field(description="Overall sentiment analysis")
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords")
    tags: List[str] = Field(default_factory=list, description="Stream tags")


class Stream(BaseModel):
    """Stream aggregate root."""

    # Identity
    id: UUID = Field(default_factory=uuid4, description="Unique stream identifier")
    video_id: str = Field(min_length=1, description="Video platform ID (e.g., YouTube video ID)")

    # Basic Information
    title: str = Field(min_length=1, max_length=500, description="Stream title")
    description: Optional[str] = Field(None, max_length=2000, description="Stream description")
    url: str = Field(description="Stream URL")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail image URL")

    # Temporal Information
    date: datetime = Field(description="Stream date")
    published_at: Optional[datetime] = Field(None, description="Published timestamp")

    # Classification
    category: StreamCategory = Field(default=StreamCategory.GENERAL, description="Stream category")
    status: StreamStatus = Field(default=StreamStatus.COMPLETED, description="Stream status")

    # Metrics and Analysis
    metrics: Optional[StreamMetrics] = Field(None, description="Stream metrics")
    analysis: Optional[StreamAnalysis] = Field(None, description="Stream analysis")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Entity creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Entity update timestamp")

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v),
        }

    def add_analysis(self, analysis: StreamAnalysis) -> None:
        """Add analysis to the stream."""
        self.analysis = analysis
        self.updated_at = datetime.utcnow()

    def update_metrics(self, metrics: StreamMetrics) -> None:
        """Update stream metrics."""
        self.metrics = metrics
        self.updated_at = datetime.utcnow()

    def categorize(self, category: StreamCategory) -> None:
        """Categorize the stream."""
        self.category = category
        self.updated_at = datetime.utcnow()

    def is_analyzed(self) -> bool:
        """Check if stream has been analyzed."""
        return self.analysis is not None

    def has_metrics(self) -> bool:
        """Check if stream has metrics."""
        return self.metrics is not None
