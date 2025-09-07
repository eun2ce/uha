"""YouTube REST controller."""

from typing import List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ..containers.di import Container
from ..entities.youtube import YouTubeChannel, YouTubeVideo
from ..services.youtube_service import YouTubeService


# Response Models
class YouTubeVideoResponse(BaseModel):
    """Response model for YouTube video."""

    video_id: str
    title: str
    description: str
    channel_title: str
    published_at: str
    view_count: int
    like_count: int
    comment_count: int
    duration: str
    thumbnail_url: Optional[str]
    tags: List[str]

    @classmethod
    def from_entity(cls, video: YouTubeVideo) -> "YouTubeVideoResponse":
        """Create response from video entity."""
        return cls(
            video_id=video.video_id,
            title=video.snippet.title,
            description=video.snippet.description or "",
            channel_title=video.snippet.channel_title,
            published_at=video.snippet.published_at.isoformat(),
            view_count=video.statistics.view_count,
            like_count=video.statistics.like_count,
            comment_count=video.statistics.comment_count,
            duration=video.content_details.duration,
            thumbnail_url=video.get_thumbnail_url(),
            tags=video.snippet.tags,
        )


class YouTubeChannelResponse(BaseModel):
    """Response model for YouTube channel."""

    channel_id: str
    title: str
    description: str
    subscriber_count: Optional[int]
    video_count: Optional[int]
    view_count: Optional[int]
    thumbnail_url: Optional[str]

    @classmethod
    def from_entity(cls, channel: YouTubeChannel) -> "YouTubeChannelResponse":
        """Create response from channel entity."""
        return cls(
            channel_id=channel.channel_id,
            title=channel.title,
            description=channel.description or "",
            subscriber_count=channel.subscriber_count,
            video_count=channel.video_count,
            view_count=channel.view_count,
            thumbnail_url=str(channel.thumbnail_url) if channel.thumbnail_url else None,
        )


# Router
router = APIRouter(prefix="/youtube", tags=["YouTube"])


@router.get("/video/{video_id}", response_model=YouTubeVideoResponse)
@inject
async def get_video(
    video_id: str, youtube_service: YouTubeService = Depends(Provide[Container.youtube_service])
) -> YouTubeVideoResponse:
    """Get YouTube video details."""
    try:
        video = await youtube_service.get_video_details(video_id)
        return YouTubeVideoResponse.from_entity(video)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch video: {str(e)}")


@router.get("/channel/{channel_id}", response_model=YouTubeChannelResponse)
@inject
async def get_channel(
    channel_id: str, youtube_service: YouTubeService = Depends(Provide[Container.youtube_service])
) -> YouTubeChannelResponse:
    """Get YouTube channel information."""
    try:
        channel = await youtube_service.get_channel_info(channel_id)
        return YouTubeChannelResponse.from_entity(channel)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch channel: {str(e)}")


@router.get("/extract-video-id")
async def extract_video_id(
    url: str = Query(description="YouTube video URL"),
    youtube_service: YouTubeService = Depends(Provide[Container.youtube_service]),
) -> dict:
    """Extract video ID from YouTube URL."""
    video_id = youtube_service.extract_video_id(url)

    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    return {"video_id": video_id, "url": url}


@router.get("/search")
@inject
async def search_videos(
    q: str = Query(description="Search query"),
    max_results: int = Query(10, ge=1, le=50, description="Maximum results"),
    channel_id: Optional[str] = Query(None, description="Filter by channel ID"),
    youtube_service: YouTubeService = Depends(Provide[Container.youtube_service]),
) -> dict:
    """Search YouTube videos."""
    try:
        results = await youtube_service.search_videos(query=q, max_results=max_results, channel_id=channel_id)

        return {"results": results, "query": q, "total_results": len(results)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
