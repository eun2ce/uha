"""YouTube API endpoints."""

from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from uha.backend.container import ApplicationContainer
from uha.backend.settings import Settings

router = APIRouter(prefix="/youtube", tags=["YouTube"])


class VideoData(BaseModel):
    title: str
    thumbnail_url: str
    video_url: str


class YouTubeChannelResponse(BaseModel):
    channel_id: str
    channel_name: str
    description: str
    custom_url: Optional[str] = None
    thumbnail_url: str
    published_at: str
    view_count: str
    subscriber_count: str
    video_count: str
    country: Optional[str] = None
    recent_videos: Optional[List[VideoData]] = None


async def get_settings() -> Settings:
    """Get application settings."""
    container = ApplicationContainer()
    return container.settings.provided()


async def get_youtube_channel_info(settings: Settings) -> Dict[str, Any]:
    """Get YouTube channel information."""
    url = "https://www.googleapis.com/youtube/v3/channels"
    params = {"id": settings.youtube_channel_id, "part": "id,snippet,statistics", "key": settings.youtube_api_key}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="YouTube API 호출 실패")

    data = response.json()
    items = data.get("items", [])

    if not items:
        raise HTTPException(status_code=404, detail="채널 정보를 찾을 수 없습니다.")

    return items[0]


async def get_recent_videos(channel_id: str, settings: Settings) -> List[VideoData]:
    """Get recent videos from the channel."""
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "channelId": channel_id,
        "order": "date",
        "part": "snippet",
        "maxResults": 4,
        "key": settings.youtube_api_key,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="최근 영상 정보를 불러오는 데 실패했습니다.")

    data = response.json()
    items = data.get("items", [])

    recent_videos = []
    for item in items:
        if item.get("id", {}).get("kind") == "youtube#video":
            video_data = VideoData(
                title=item["snippet"]["title"],
                thumbnail_url=item["snippet"]["thumbnails"]["high"]["url"],
                video_url=f"https://www.youtube.com/watch?v={item['id']['videoId']}",
            )
            recent_videos.append(video_data)

    return recent_videos


@router.get("/channel-info", response_model=YouTubeChannelResponse)
async def get_channel_info(settings: Settings = Depends(get_settings)):
    """Get YouTube channel information with recent videos."""
    try:
        # Get channel info
        channel_info = await get_youtube_channel_info(settings)

        # Get recent videos
        recent_videos = await get_recent_videos(channel_info["id"], settings)

        # Format response
        response_data = {
            "channel_id": channel_info["id"],
            "channel_name": channel_info["snippet"]["title"],
            "description": channel_info["snippet"]["description"],
            "custom_url": channel_info["snippet"].get("customUrl"),
            "thumbnail_url": channel_info["snippet"]["thumbnails"]["high"]["url"],
            "published_at": channel_info["snippet"]["publishedAt"],
            "view_count": channel_info["statistics"]["viewCount"],
            "subscriber_count": channel_info["statistics"]["subscriberCount"],
            "video_count": channel_info["statistics"]["videoCount"],
            "country": channel_info["snippet"].get("country"),
            "recent_videos": recent_videos,
        }

        return YouTubeChannelResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")
