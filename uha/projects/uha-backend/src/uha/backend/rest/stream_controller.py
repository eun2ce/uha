"""Stream REST controller."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from ..containers.di import Container
from ..entities.stream import Stream, StreamCategory
from ..services.stream_service import StreamService


# Request/Response Models
class StreamCreateRequest(BaseModel):
    """Request model for creating a stream."""

    url: str = Field(min_length=1, description="Stream URL")
    date: datetime = Field(description="Stream date")


class StreamResponse(BaseModel):
    """Response model for stream."""

    id: UUID
    video_id: str
    title: str
    description: Optional[str]
    url: str
    thumbnail_url: Optional[str]
    date: datetime
    published_at: Optional[datetime]
    category: StreamCategory

    # Metrics
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    duration_minutes: Optional[int] = None
    engagement_score: Optional[float] = None

    # Analysis
    ai_summary: Optional[str] = None
    highlights: Optional[List[str]] = None
    sentiment: Optional[str] = None
    keywords: Optional[List[str]] = None
    tags: Optional[List[str]] = None

    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, stream: Stream) -> "StreamResponse":
        """Create response from stream entity."""
        return cls(
            id=stream.id,
            video_id=stream.video_id,
            title=stream.title,
            description=stream.description,
            url=stream.url,
            thumbnail_url=stream.thumbnail_url,
            date=stream.date,
            published_at=stream.published_at,
            category=stream.category,
            view_count=stream.metrics.view_count if stream.metrics else None,
            like_count=stream.metrics.like_count if stream.metrics else None,
            comment_count=stream.metrics.comment_count if stream.metrics else None,
            duration_minutes=stream.metrics.duration_minutes if stream.metrics else None,
            engagement_score=float(stream.metrics.engagement_score) if stream.metrics else None,
            ai_summary=stream.analysis.ai_summary if stream.analysis else None,
            highlights=stream.analysis.highlights if stream.analysis else None,
            sentiment=stream.analysis.sentiment if stream.analysis else None,
            keywords=stream.analysis.keywords if stream.analysis else None,
            tags=stream.analysis.tags if stream.analysis else None,
            created_at=stream.created_at,
            updated_at=stream.updated_at,
        )


class PaginatedStreamsResponse(BaseModel):
    """Paginated streams response."""

    streams: List[StreamResponse]
    total_streams: int
    current_page: int
    total_pages: int
    per_page: int


# Router
router = APIRouter(prefix="/streams", tags=["Streams"])


@router.post("/", response_model=StreamResponse)
@inject
async def create_stream(
    request: StreamCreateRequest,
    stream_service: StreamService = Depends(Provide[Container.stream_service]),
) -> StreamResponse:
    """Create a new stream."""
    try:
        # Create stream from URL
        stream = await stream_service.create_stream_from_url(request.url, request.date)

        # Enrich with YouTube data
        enriched_stream = await stream_service.enrich_stream_with_youtube_data(stream)

        # Analyze with AI
        analyzed_stream = await stream_service.analyze_stream_with_ai(enriched_stream)

        return StreamResponse.from_entity(analyzed_stream)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/", response_model=PaginatedStreamsResponse)
@inject
async def get_streams(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(12, ge=1, le=100, description="Items per page"),
    category: Optional[StreamCategory] = Query(None, description="Filter by category"),
    stream_service: StreamService = Depends(Provide[Container.stream_service]),
) -> PaginatedStreamsResponse:
    """Get paginated list of streams."""
    # This would typically fetch from a database
    # For now, return empty response
    return PaginatedStreamsResponse(streams=[], total_streams=0, current_page=page, total_pages=0, per_page=per_page)


@router.get("/categories", response_model=List[str])
async def get_categories() -> List[str]:
    """Get available stream categories."""
    return [category.value for category in StreamCategory]


@router.post("/batch", response_model=List[StreamResponse])
@inject
async def create_streams_batch(
    requests: List[StreamCreateRequest],
    stream_service: StreamService = Depends(Provide[Container.stream_service]),
) -> List[StreamResponse]:
    """Create multiple streams in batch."""
    try:
        # Create streams
        streams = []
        for req in requests:
            stream = await stream_service.create_stream_from_url(req.url, req.date)
            streams.append(stream)

        # Process batch
        processed_streams = await stream_service.process_streams_batch(streams)

        # Convert to responses
        responses = [StreamResponse.from_entity(stream) for stream in processed_streams]

        return responses

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")


@router.get("/{stream_id}", response_model=StreamResponse)
@inject
async def get_stream(
    stream_id: UUID, stream_service: StreamService = Depends(Provide[Container.stream_service])
) -> StreamResponse:
    """Get a specific stream by ID."""
    # This would typically fetch from a database
    raise HTTPException(status_code=404, detail="Stream not found")


@router.put("/{stream_id}/analyze", response_model=StreamResponse)
@inject
async def analyze_stream(
    stream_id: UUID, stream_service: StreamService = Depends(Provide[Container.stream_service])
) -> StreamResponse:
    """Analyze an existing stream with AI."""
    # This would typically fetch the stream from database first
    raise HTTPException(status_code=404, detail="Stream not found")
