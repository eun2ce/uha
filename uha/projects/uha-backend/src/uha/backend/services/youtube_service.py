"""YouTube Service for API integration."""

from typing import Dict, List, Optional

import httpx
from pydantic import BaseModel, Field

from ..entities.youtube import (
    YouTubeChannel,
    YouTubeComment,
    YouTubeVideo,
    YouTubeVideoContentDetails,
    YouTubeVideoSnippet,
    YouTubeVideoStatistics,
)


class YouTubeServiceConfig(BaseModel):
    """YouTube Service configuration."""

    api_key: str = Field(min_length=1, description="YouTube Data API key")
    base_url: str = Field(default="https://www.googleapis.com/youtube/v3", description="API base URL")
    timeout_seconds: int = Field(default=30, ge=1, description="Request timeout")
    max_results_per_request: int = Field(default=50, ge=1, le=100, description="Max results per request")


class YouTubeService:
    """YouTube Service for API operations."""

    def __init__(self, config: YouTubeServiceConfig):
        """Initialize YouTube Service."""
        self.config = config
        self._client = None

    def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(base_url=self.config.base_url, timeout=self.config.timeout_seconds)
        return self._client

    async def get_video_details(self, video_id: str) -> YouTubeVideo:
        """Get detailed video information."""
        client = self._get_client()

        params = {"id": video_id, "part": "snippet,statistics,contentDetails", "key": self.config.api_key}

        response = await client.get("/videos", params=params)
        response.raise_for_status()

        data = response.json()
        items = data.get("items", [])

        if not items:
            raise ValueError(f"Video not found: {video_id}")

        item = items[0]

        # Parse snippet
        snippet_data = item["snippet"]
        snippet = YouTubeVideoSnippet(
            title=snippet_data["title"],
            description=snippet_data.get("description", ""),
            published_at=snippet_data["publishedAt"],
            channel_id=snippet_data["channelId"],
            channel_title=snippet_data["channelTitle"],
            tags=snippet_data.get("tags", []),
            category_id=snippet_data.get("categoryId"),
            default_language=snippet_data.get("defaultLanguage"),
            thumbnails=snippet_data.get("thumbnails", {}),
        )

        # Parse statistics
        stats_data = item["statistics"]
        statistics = YouTubeVideoStatistics(
            view_count=int(stats_data.get("viewCount", 0)),
            like_count=int(stats_data.get("likeCount", 0)),
            comment_count=int(stats_data.get("commentCount", 0)),
            favorite_count=int(stats_data.get("favoriteCount", 0)),
        )

        # Parse content details
        content_data = item["contentDetails"]
        content_details = YouTubeVideoContentDetails(
            duration=content_data["duration"],
            dimension=content_data.get("dimension"),
            definition=content_data.get("definition"),
            caption=content_data.get("caption"),
            licensed_content=content_data.get("licensedContent"),
            projection=content_data.get("projection"),
        )

        return YouTubeVideo(video_id=video_id, snippet=snippet, statistics=statistics, content_details=content_details)

    async def get_video_comments(
        self, video_id: str, max_results: int = 20, order: str = "relevance"
    ) -> List[YouTubeComment]:
        """Get video comments."""
        try:
            client = self._get_client()

            params = {
                "videoId": video_id,
                "part": "snippet",
                "maxResults": min(max_results, self.config.max_results_per_request),
                "order": order,
                "key": self.config.api_key,
            }

            response = await client.get("/commentThreads", params=params)

            if response.status_code != 200:
                # Comments might be disabled
                return []

            data = response.json()
            items = data.get("items", [])

            comments = []
            for item in items:
                comment_data = item["snippet"]["topLevelComment"]["snippet"]
                comment = YouTubeComment(
                    id=item["snippet"]["topLevelComment"]["id"],
                    author_display_name=comment_data["authorDisplayName"],
                    author_profile_image_url=comment_data.get("authorProfileImageUrl"),
                    text_display=comment_data["textDisplay"],
                    like_count=comment_data.get("likeCount", 0),
                    published_at=comment_data["publishedAt"],
                    updated_at=comment_data.get("updatedAt"),
                )
                comments.append(comment)

            return comments

        except Exception as e:
            print(f"Error fetching comments for {video_id}: {str(e)}")
            return []

    async def get_channel_info(self, channel_id: str) -> YouTubeChannel:
        """Get channel information."""
        client = self._get_client()

        params = {"id": channel_id, "part": "snippet,statistics", "key": self.config.api_key}

        response = await client.get("/channels", params=params)
        response.raise_for_status()

        data = response.json()
        items = data.get("items", [])

        if not items:
            raise ValueError(f"Channel not found: {channel_id}")

        item = items[0]
        snippet = item["snippet"]
        statistics = item["statistics"]

        return YouTubeChannel(
            channel_id=channel_id,
            title=snippet["title"],
            description=snippet.get("description", ""),
            custom_url=snippet.get("customUrl"),
            subscriber_count=int(statistics.get("subscriberCount", 0)),
            video_count=int(statistics.get("videoCount", 0)),
            view_count=int(statistics.get("viewCount", 0)),
            thumbnail_url=snippet.get("thumbnails", {}).get("high", {}).get("url"),
        )

    async def search_videos(
        self, query: str, max_results: int = 10, order: str = "relevance", channel_id: Optional[str] = None
    ) -> List[Dict]:
        """Search for videos."""
        client = self._get_client()

        params = {
            "q": query,
            "part": "snippet",
            "type": "video",
            "maxResults": min(max_results, self.config.max_results_per_request),
            "order": order,
            "key": self.config.api_key,
        }

        if channel_id:
            params["channelId"] = channel_id

        response = await client.get("/search", params=params)
        response.raise_for_status()

        data = response.json()
        return data.get("items", [])

    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL."""
        import re

        patterns = [
            r"(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})",
            r"youtube\.com\/embed\/([a-zA-Z0-9_-]{11})",
            r"youtube\.com\/v\/([a-zA-Z0-9_-]{11})",
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
