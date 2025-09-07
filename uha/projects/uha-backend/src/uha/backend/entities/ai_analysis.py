"""AI Analysis domain entities."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class SentimentType(str, Enum):
    """Sentiment type enumeration."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class KeywordType(str, Enum):
    """Keyword type enumeration."""

    EXTRACTED = "extracted"  # From content analysis
    TAGGED = "tagged"  # From user tags
    GENERATED = "generated"  # AI generated


class Sentiment(BaseModel):
    """Sentiment analysis value object."""

    type: SentimentType = Field(description="Sentiment type")
    score: Decimal = Field(ge=0, le=1, description="Sentiment confidence score")
    description: str = Field(min_length=1, max_length=200, description="Sentiment description")

    @validator("score")
    def validate_score(cls, v):
        """Validate sentiment score."""
        return round(v, 3)


class Keyword(BaseModel):
    """Keyword value object."""

    text: str = Field(min_length=1, max_length=50, description="Keyword text")
    type: KeywordType = Field(description="Keyword type")
    frequency: int = Field(ge=1, description="Keyword frequency")
    relevance_score: Decimal = Field(ge=0, le=1, description="Relevance score")

    @validator("relevance_score")
    def validate_relevance_score(cls, v):
        """Validate relevance score."""
        return round(v, 3)


class AIAnalysis(BaseModel):
    """AI Analysis aggregate root."""

    # Identity
    id: UUID = Field(default_factory=uuid4, description="Analysis identifier")
    target_id: str = Field(min_length=1, description="Target entity ID (e.g., video_id)")
    target_type: str = Field(min_length=1, description="Target entity type")

    # Analysis Results
    summary: str = Field(min_length=1, max_length=1000, description="AI-generated summary")
    highlights: List[str] = Field(default_factory=list, description="Extracted highlights")
    sentiment: Sentiment = Field(description="Sentiment analysis")
    keywords: List[Keyword] = Field(default_factory=list, description="Extracted keywords")

    # Analysis Metadata
    model_name: str = Field(min_length=1, description="AI model used")
    model_version: Optional[str] = Field(None, description="Model version")
    confidence_score: Decimal = Field(ge=0, le=1, description="Overall confidence score")
    processing_time_ms: int = Field(ge=0, description="Processing time in milliseconds")

    # Additional Data
    raw_response: Optional[Dict] = Field(None, description="Raw AI model response")
    metadata: Dict = Field(default_factory=dict, description="Additional metadata")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v),
        }

    @validator("confidence_score")
    def validate_confidence_score(cls, v):
        """Validate confidence score."""
        return round(v, 3)

    def add_keyword(self, keyword: Keyword) -> None:
        """Add a keyword to the analysis."""
        self.keywords.append(keyword)
        self.updated_at = datetime.utcnow()

    def add_keywords(self, keywords: List[Keyword]) -> None:
        """Add multiple keywords to the analysis."""
        self.keywords.extend(keywords)
        self.updated_at = datetime.utcnow()

    def get_keywords_by_type(self, keyword_type: KeywordType) -> List[Keyword]:
        """Get keywords filtered by type."""
        return [kw for kw in self.keywords if kw.type == keyword_type]

    def get_top_keywords(self, limit: int = 10) -> List[Keyword]:
        """Get top keywords by relevance score."""
        return sorted(self.keywords, key=lambda kw: kw.relevance_score, reverse=True)[:limit]

    def is_positive_sentiment(self) -> bool:
        """Check if sentiment is positive."""
        return self.sentiment.type == SentimentType.POSITIVE

    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """Check if analysis has high confidence."""
        return float(self.confidence_score) >= threshold
