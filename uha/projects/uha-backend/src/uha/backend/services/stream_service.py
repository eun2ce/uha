"""Stream Service for business logic."""

import asyncio
from decimal import Decimal
from typing import List

from pydantic import BaseModel, Field

from ..entities.stream import Stream, StreamAnalysis, StreamCategory, StreamMetrics
from .ai_service import AIService, SummaryRequest
from .youtube_service import YouTubeService


class StreamServiceConfig(BaseModel):
    """Stream Service configuration."""

    max_concurrent_analysis: int = Field(default=5, ge=1, description="Max concurrent analysis tasks")
    default_category: StreamCategory = Field(default=StreamCategory.GENERAL, description="Default category")


class StreamService:
    """Stream Service for business operations."""

    def __init__(self, config: StreamServiceConfig, ai_service: AIService, youtube_service: YouTubeService):
        """Initialize Stream Service."""
        self.config = config
        self.ai_service = ai_service
        self.youtube_service = youtube_service

    async def create_stream_from_url(self, url: str, date: str) -> Stream:
        """Create stream from URL."""
        # Extract video ID
        video_id = self.youtube_service.extract_video_id(url)
        if not video_id:
            raise ValueError(f"Invalid YouTube URL: {url}")

        # Create basic stream
        stream = Stream(
            video_id=video_id, title=f"Stream - {date}", url=url, date=date, category=self.config.default_category
        )

        return stream

    async def enrich_stream_with_youtube_data(self, stream: Stream) -> Stream:
        """Enrich stream with YouTube data."""
        try:
            # Get video details
            youtube_video = await self.youtube_service.get_video_details(stream.video_id)

            # Update stream with YouTube data
            stream.title = youtube_video.snippet.title
            stream.description = youtube_video.snippet.description
            stream.thumbnail_url = youtube_video.get_thumbnail_url("high")
            stream.published_at = youtube_video.snippet.published_at

            # Create metrics
            metrics = StreamMetrics(
                view_count=youtube_video.statistics.view_count,
                like_count=youtube_video.statistics.like_count,
                comment_count=youtube_video.statistics.comment_count,
                duration_minutes=youtube_video.get_duration_minutes(),
                engagement_score=self._calculate_engagement_score(
                    youtube_video.statistics.view_count,
                    youtube_video.statistics.like_count,
                    youtube_video.statistics.comment_count,
                    youtube_video.get_duration_minutes(),
                ),
            )

            stream.update_metrics(metrics)

            # Categorize stream
            category = self._categorize_stream(
                youtube_video.snippet.title, youtube_video.snippet.tags, youtube_video.snippet.description or ""
            )
            stream.categorize(category)

            return stream

        except Exception as e:
            print(f"Error enriching stream {stream.video_id}: {str(e)}")
            return stream

    async def analyze_stream_with_ai(self, stream: Stream) -> Stream:
        """Analyze stream with AI."""
        try:
            # Get YouTube data first if not available
            if not stream.has_metrics():
                stream = await self.enrich_stream_with_youtube_data(stream)

            # Get comments for analysis
            comments = await self.youtube_service.get_video_comments(stream.video_id, max_results=20)
            comment_texts = [comment.text_display for comment in comments]

            # Prepare AI request
            ai_request = SummaryRequest(
                title=stream.title,
                description=stream.description or "",
                comments=comment_texts,
                tags=stream.analysis.tags if stream.analysis else [],
                keywords=[],
            )

            # Generate AI analysis
            ai_analysis = await self.ai_service.create_full_analysis(
                target_id=stream.video_id, target_type="stream", request=ai_request
            )

            # Create stream analysis
            analysis = StreamAnalysis(
                ai_summary=ai_analysis.summary,
                highlights=ai_analysis.highlights,
                sentiment=ai_analysis.sentiment.description,
                keywords=[kw.text for kw in ai_analysis.get_top_keywords(10)],
                tags=[],  # Will be populated from YouTube data
            )

            stream.add_analysis(analysis)

            return stream

        except Exception as e:
            print(f"Error analyzing stream {stream.video_id}: {str(e)}")
            return stream

    async def process_streams_batch(self, streams: List[Stream]) -> List[Stream]:
        """Process multiple streams with concurrency control."""
        semaphore = asyncio.Semaphore(self.config.max_concurrent_analysis)

        async def process_single_stream(stream: Stream) -> Stream:
            async with semaphore:
                # Enrich with YouTube data
                enriched_stream = await self.enrich_stream_with_youtube_data(stream)

                # Analyze with AI
                analyzed_stream = await self.analyze_stream_with_ai(enriched_stream)

                return analyzed_stream

        # Process all streams concurrently
        tasks = [process_single_stream(stream) for stream in streams]
        processed_streams = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        result_streams = []
        for result in processed_streams:
            if isinstance(result, Exception):
                print(f"Error processing stream: {result}")
            else:
                result_streams.append(result)

        return result_streams

    def _calculate_engagement_score(
        self, view_count: int, like_count: int, comment_count: int, duration_minutes: int
    ) -> Decimal:
        """Calculate engagement score."""
        if view_count == 0:
            return Decimal("0.0")

        # Basic engagement calculation
        like_rate = (like_count / view_count) * 100
        comment_rate = (comment_count / view_count) * 100

        # Duration factor (longer streams get slight bonus)
        duration_factor = min(duration_minutes / 60, 3)  # Max 3 hours bonus

        engagement_score = (like_rate * 0.6 + comment_rate * 0.4) * (1 + duration_factor * 0.1)

        return Decimal(str(round(min(engagement_score, 10.0), 2)))

    def _categorize_stream(self, title: str, tags: List[str], description: str) -> StreamCategory:
        """Categorize stream based on content."""
        all_text = f"{title} {' '.join(tags)} {description}".lower()

        categories = {
            StreamCategory.GAMING: ["게임", "game", "플레이", "play", "rpg", "fps", "moba"],
            StreamCategory.MUSIC: ["음악", "music", "노래", "song", "sing", "cover"],
            StreamCategory.TALK: ["토크", "talk", "채팅", "chat", "소통", "qa", "질문"],
            StreamCategory.ART: ["그림", "draw", "art", "창작", "만들기", "diy"],
            StreamCategory.EDUCATION: ["강의", "교육", "tutorial", "배우기", "learn", "study"],
            StreamCategory.COOKING: ["요리", "cook", "먹방", "food", "recipe"],
            StreamCategory.FITNESS: ["운동", "workout", "fitness", "헬스", "스포츠"],
            StreamCategory.REVIEW: ["리뷰", "review", "후기", "평가", "반응"],
        }

        for category, keywords in categories.items():
            if any(keyword in all_text for keyword in keywords):
                return category

        return StreamCategory.GENERAL
