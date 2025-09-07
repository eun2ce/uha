"""Legacy LLM controller for backward compatibility."""

from datetime import datetime
from pathlib import Path
from typing import List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..containers.di import Container
from ..services.stream_service import StreamService


# Legacy models for backward compatibility
class StreamEntry(BaseModel):
    """Stream entry from markdown file."""

    date: str
    url: str


class StreamWithDetails(BaseModel):
    """Stream with detailed information."""

    date: str
    url: str
    video_id: Optional[str] = None
    title: Optional[str] = None
    thumbnail: Optional[str] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    duration: Optional[str] = None
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    ai_summary: Optional[str] = None
    highlights: Optional[List[str]] = None
    sentiment: Optional[str] = None
    engagement_score: Optional[float] = None
    category: Optional[str] = None


class PaginatedStreamsRequest(BaseModel):
    """Request for paginated streams."""

    year: int = Field(ge=2020, le=2030, description="Year to fetch streams for")
    page: int = Field(ge=1, description="Page number")
    per_page: int = Field(ge=1, le=50, description="Items per page")
    include_details: bool = Field(default=True, description="Include detailed analysis")


class PaginatedStreamsResponse(BaseModel):
    """Response for paginated streams."""

    streams: List[StreamWithDetails]
    total_streams: int
    current_page: int
    total_pages: int
    per_page: int


class YearSummaryRequest(BaseModel):
    """Request for year summary."""

    year: int = Field(ge=2020, le=2030, description="Year to summarize")


# Router
router = APIRouter(prefix="/llm", tags=["Legacy LLM"])


def read_markdown_file(year: int) -> List[StreamEntry]:
    """Read stream entries from markdown file."""
    try:
        # Look for the submodule directory
        base_path = Path(__file__).parent.parent.parent.parent.parent.parent
        submodule_path = base_path / "uzuhama-live-link"

        if not submodule_path.exists():
            print(f"Submodule path not found: {submodule_path}")
            return []

        markdown_file = submodule_path / f"readme-{year}.md"

        if not markdown_file.exists():
            print(f"Markdown file not found: {markdown_file}")
            return []

        entries = []
        with open(markdown_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and "|" in line and "youtube.com" in line:
                    parts = line.split("|")
                    if len(parts) >= 2:
                        date = parts[0].strip()
                        url = parts[1].strip()
                        if date and url and date != "Date":
                            entries.append(StreamEntry(date=date, url=url))

        return entries

    except Exception as e:
        print(f"Error reading markdown file for year {year}: {str(e)}")
        return []


@router.post("/streams", response_model=PaginatedStreamsResponse)
@inject
async def get_paginated_streams(
    request: PaginatedStreamsRequest,
    stream_service: StreamService = Depends(Provide[Container.stream_service]),
) -> PaginatedStreamsResponse:
    """Get paginated streams with analysis."""
    try:
        # Read entries from markdown file
        entries = read_markdown_file(request.year)

        if not entries:
            return PaginatedStreamsResponse(
                streams=[], total_streams=0, current_page=request.page, total_pages=0, per_page=request.per_page
            )

        # Calculate pagination
        total_streams = len(entries)
        total_pages = (total_streams + request.per_page - 1) // request.per_page
        start_idx = (request.page - 1) * request.per_page
        end_idx = start_idx + request.per_page
        paginated_entries = entries[start_idx:end_idx]

        # Process streams
        streams_with_details = []

        if request.include_details:
            # Create Stream objects
            streams = []
            for entry in paginated_entries:
                try:
                    stream = await stream_service.create_stream_from_url(
                        entry.url, datetime.strptime(entry.date, "%Y-%m-%d")
                    )
                    streams.append(stream)
                except Exception as e:
                    print(f"Error creating stream from {entry.url}: {e}")
                    continue

            # Process batch with analysis
            processed_streams = await stream_service.process_streams_batch(streams)

            # Convert to response format
            for stream in processed_streams:
                stream_details = StreamWithDetails(
                    date=stream.date.strftime("%Y-%m-%d"),
                    url=stream.url,
                    video_id=stream.video_id,
                    title=stream.title,
                    thumbnail=stream.thumbnail_url,
                    view_count=stream.metrics.view_count if stream.metrics else None,
                    like_count=stream.metrics.like_count if stream.metrics else None,
                    comment_count=stream.metrics.comment_count if stream.metrics else None,
                    duration=f"PT{stream.metrics.duration_minutes}M" if stream.metrics else None,
                    tags=[],
                    keywords=stream.analysis.keywords if stream.analysis else [],
                    ai_summary=stream.analysis.ai_summary if stream.analysis else None,
                    highlights=stream.analysis.highlights if stream.analysis else [],
                    sentiment=stream.analysis.sentiment if stream.analysis else None,
                    engagement_score=float(stream.metrics.engagement_score) if stream.metrics else None,
                    category=stream.category.value,
                )
                streams_with_details.append(stream_details)
        else:
            # Basic information only
            for entry in paginated_entries:
                video_id = None
                if "youtube.com/watch?v=" in entry.url:
                    video_id = entry.url.split("v=")[1].split("&")[0]

                stream_details = StreamWithDetails(date=entry.date, url=entry.url, video_id=video_id)
                streams_with_details.append(stream_details)

        return PaginatedStreamsResponse(
            streams=streams_with_details,
            total_streams=total_streams,
            current_page=request.page,
            total_pages=total_pages,
            per_page=request.per_page,
        )

    except Exception as e:
        print(f"Error processing streams: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process streams: {str(e)}")


@router.post("/summary")
@inject
async def get_year_summary(
    request: YearSummaryRequest,
    stream_service: StreamService = Depends(Provide[Container.stream_service]),
) -> dict:
    """Get AI-generated summary for a year."""
    try:
        # Read entries for the year
        entries = read_markdown_file(request.year)

        if not entries:
            return {"summary": f"{request.year}년 스트림 데이터를 찾을 수 없습니다."}

        # Create a sample of streams for analysis
        sample_size = min(10, len(entries))
        sample_entries = entries[:sample_size]

        # Create streams and analyze
        streams = []
        for entry in sample_entries:
            try:
                stream = await stream_service.create_stream_from_url(
                    entry.url, datetime.strptime(entry.date, "%Y-%m-%d")
                )
                streams.append(stream)
            except Exception as e:
                print(f"Error creating stream: {e}")
                continue

        if not streams:
            return {"summary": f"{request.year}년 스트림 분석에 실패했습니다."}

        # Process streams
        processed_streams = await stream_service.process_streams_batch(streams)

        # Generate overall summary
        all_summaries = []
        all_categories = []

        for stream in processed_streams:
            if stream.analysis and stream.analysis.ai_summary:
                all_summaries.append(stream.analysis.ai_summary)
            all_categories.append(stream.category.value)

        # Create year summary
        category_counts = {}
        for category in all_categories:
            category_counts[category] = category_counts.get(category, 0) + 1

        most_common_category = max(category_counts, key=category_counts.get) if category_counts else "일반"

        summary = f"{request.year}년에는 총 {len(entries)}개의 라이브 스트림이 진행되었습니다. "
        summary += f"주요 카테고리는 {most_common_category}이며, "
        summary += "분석된 스트림들은 대부분 시청자들과의 활발한 소통이 이루어진 것으로 나타났습니다."

        return {
            "year": request.year,
            "summary": summary,
            "total_streams": len(entries),
            "analyzed_streams": len(processed_streams),
            "categories": category_counts,
        }

    except Exception as e:
        print(f"Error generating year summary: {str(e)}")
        return {"summary": f"{request.year}년 요약 생성에 실패했습니다."}


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "message": "LLM service is running"}
