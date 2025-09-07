"""Stream caching service using SQLite."""

import json
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import select, update

from ..database.models import DatabaseManager, StreamCache
from ..models.stream_models import StreamWithDetails


class StreamCacheService:
    """Service for caching stream data to avoid repeated API calls."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.cache_duration_hours = 24  # Cache for 24 hours

    async def get_cached_stream(self, video_id: str) -> Optional[StreamWithDetails]:
        """Get cached stream data if available and not expired."""
        session = self.db_manager.get_session()
        try:
            # Get cached data
            stmt = select(StreamCache).where(StreamCache.video_id == video_id)
            result = await session.execute(stmt)
            cached_stream = result.scalar_one_or_none()

            if not cached_stream:
                return None

            # Check if cache is expired
            cache_age = datetime.utcnow() - cached_stream.updated_at
            if cache_age > timedelta(hours=self.cache_duration_hours):
                return None

            # Update last accessed time
            await session.execute(
                update(StreamCache).where(StreamCache.video_id == video_id).values(last_accessed=datetime.utcnow())
            )
            await session.commit()

            # Convert to StreamWithDetails
            return self._cache_to_stream_details(cached_stream)
        finally:
            await session.close()

    async def cache_stream(self, stream: StreamWithDetails) -> None:
        """Cache stream data."""
        session = self.db_manager.get_session()
        try:
            # Check if already exists
            stmt = select(StreamCache).where(StreamCache.video_id == stream.video_id)
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing record
                await session.execute(
                    update(StreamCache)
                    .where(StreamCache.video_id == stream.video_id)
                    .values(
                        url=stream.url,
                        date=stream.date,
                        title=stream.title,
                        thumbnail=stream.thumbnail,
                        view_count=stream.view_count,
                        like_count=stream.like_count,
                        comment_count=stream.comment_count,
                        duration=stream.duration,
                        ai_summary=stream.ai_summary,
                        highlights=json.dumps(stream.highlights or []),
                        sentiment=stream.sentiment,
                        engagement_score=stream.engagement_score,
                        category=stream.category,
                        tags=json.dumps(stream.tags or []),
                        keywords=json.dumps(stream.keywords or []),
                        updated_at=datetime.utcnow(),
                        last_accessed=datetime.utcnow(),
                    )
                )
            else:
                # Create new record
                cache_entry = StreamCache(
                    video_id=stream.video_id,
                    url=stream.url,
                    date=stream.date,
                    title=stream.title,
                    thumbnail=stream.thumbnail,
                    view_count=stream.view_count,
                    like_count=stream.like_count,
                    comment_count=stream.comment_count,
                    duration=stream.duration,
                    ai_summary=stream.ai_summary,
                    highlights=json.dumps(stream.highlights or []),
                    sentiment=stream.sentiment,
                    engagement_score=stream.engagement_score,
                    category=stream.category,
                    tags=json.dumps(stream.tags or []),
                    keywords=json.dumps(stream.keywords or []),
                )
                session.add(cache_entry)

            await session.commit()
        finally:
            await session.close()

    async def get_cached_streams_by_year(self, year: int, page: int = 1, per_page: int = 10) -> List[StreamWithDetails]:
        """Get cached streams for a specific year with pagination."""
        session = self.db_manager.get_session()
        try:
            year_filter = f"{year}-"
            offset = (page - 1) * per_page

            stmt = (
                select(StreamCache)
                .where(StreamCache.date.like(f"{year_filter}%"))
                .order_by(StreamCache.date.desc())
                .offset(offset)
                .limit(per_page)
            )

            result = await session.execute(stmt)
            cached_streams = result.scalars().all()

            return [self._cache_to_stream_details(cached) for cached in cached_streams]
        finally:
            await session.close()

    async def get_cached_stream_count(self, year: int) -> int:
        """Get total count of cached streams for a year."""
        session = self.db_manager.get_session()
        try:
            year_filter = f"{year}-"

            stmt = select(StreamCache).where(StreamCache.date.like(f"{year_filter}%"))
            result = await session.execute(stmt)
            return len(result.scalars().all())
        finally:
            await session.close()

    async def clear_expired_cache(self) -> int:
        """Clear expired cache entries and return count of deleted entries."""
        session = self.db_manager.get_session()
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=self.cache_duration_hours * 2)  # Keep for 48 hours

            # Count entries to delete
            count_stmt = select(StreamCache).where(StreamCache.last_accessed < cutoff_time)
            count_result = await session.execute(count_stmt)
            delete_count = len(count_result.scalars().all())

            # Delete expired entries
            from sqlalchemy import delete

            delete_stmt = delete(StreamCache).where(StreamCache.last_accessed < cutoff_time)
            await session.execute(delete_stmt)
            await session.commit()

            return delete_count
        finally:
            await session.close()

    def _cache_to_stream_details(self, cached: StreamCache) -> StreamWithDetails:
        """Convert cached database record to StreamWithDetails."""
        return StreamWithDetails(
            date=cached.date,
            url=cached.url,
            video_id=cached.video_id,
            title=cached.title,
            thumbnail=cached.thumbnail,
            view_count=cached.view_count,
            like_count=cached.like_count,
            comment_count=cached.comment_count,
            duration=cached.duration,
            tags=json.loads(cached.tags) if cached.tags else None,
            keywords=json.loads(cached.keywords) if cached.keywords else None,
            ai_summary=cached.ai_summary,
            highlights=json.loads(cached.highlights) if cached.highlights else None,
            sentiment=cached.sentiment,
            engagement_score=cached.engagement_score,
            category=cached.category,
        )
