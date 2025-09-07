"""SQLite database models for caching stream data."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class StreamCache(Base):
    """Cache table for stream data to avoid repeated API calls."""

    __tablename__ = "stream_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String(11), unique=True, nullable=False, index=True)
    url = Column(String(255), nullable=False)
    date = Column(String(10), nullable=False)

    # Basic video information
    title = Column(String(500))
    thumbnail = Column(String(500))
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    duration = Column(String(50))

    # AI-generated content
    ai_summary = Column(Text)
    highlights = Column(Text)  # JSON string
    sentiment = Column(String(100))
    engagement_score = Column(Float)
    category = Column(String(100))

    # Tags and keywords
    tags = Column(Text)  # JSON string
    keywords = Column(Text)  # JSON string

    # Cache metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    cache_version = Column(Integer, default=1)  # For cache invalidation


class DatabaseManager:
    """Async database manager for SQLite."""

    def __init__(self, database_url: str = "sqlite+aiosqlite:///./stream_cache.db"):
        self.database_url = database_url
        self.engine = create_async_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)

    async def create_tables(self):
        """Create database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    def get_session(self) -> AsyncSession:
        """Get database session."""
        return self.SessionLocal()

    async def close(self):
        """Close database connection."""
        await self.engine.dispose()
