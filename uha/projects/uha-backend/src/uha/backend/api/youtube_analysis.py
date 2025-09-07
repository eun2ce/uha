"""YouTube Data API를 활용한 상세 영상 분석 API."""

import re
from typing import Any, Dict, List

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from uha.backend.container import ApplicationContainer
from uha.backend.settings import Settings

router = APIRouter(prefix="/youtube-analysis", tags=["YouTube Analysis"])


class VideoStatistics(BaseModel):
    view_count: int
    like_count: int
    comment_count: int
    duration: str
    published_at: str


class VideoComment(BaseModel):
    author: str
    text: str
    like_count: int
    published_at: str


class VideoAnalysis(BaseModel):
    video_id: str
    title: str
    description: str
    tags: List[str]
    statistics: VideoStatistics
    top_comments: List[VideoComment]
    extracted_keywords: List[str]
    sentiment_summary: str


class StreamAnalysisRequest(BaseModel):
    video_urls: List[str]
    extract_comments: bool = True
    max_comments: int = 50


class StreamAnalysisResponse(BaseModel):
    videos: List[VideoAnalysis]
    summary: str
    common_keywords: List[str]
    total_engagement: Dict[str, int]


async def get_settings() -> Settings:
    """Get application settings."""
    container = ApplicationContainer()
    return container.settings.provided()


def extract_video_id(url: str) -> str:
    """Extract video ID from YouTube URL."""
    patterns = [
        r"(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})",
        r"youtube\.com\/embed\/([a-zA-Z0-9_-]{11})",
        r"youtube\.com\/v\/([a-zA-Z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    raise ValueError(f"Invalid YouTube URL: {url}")


async def get_video_details(video_id: str, api_key: str) -> Dict[str, Any]:
    """Get detailed video information from YouTube Data API."""
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {"id": video_id, "part": "snippet,statistics,contentDetails", "key": api_key}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail=f"YouTube API 호출 실패: {response.status_code}")

    data = response.json()
    items = data.get("items", [])

    if not items:
        raise HTTPException(status_code=404, detail=f"비디오를 찾을 수 없습니다: {video_id}")

    return items[0]


async def get_video_comments(video_id: str, api_key: str, max_results: int = 50) -> List[Dict[str, Any]]:
    """Get video comments from YouTube Data API."""
    url = "https://www.googleapis.com/youtube/v3/commentThreads"
    params = {
        "videoId": video_id,
        "part": "snippet",
        "maxResults": min(max_results, 100),
        "order": "relevance",
        "key": api_key,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)

        if response.status_code != 200:
            # 댓글이 비활성화된 경우 빈 리스트 반환
            return []

        data = response.json()
        return data.get("items", [])

    except Exception:
        # 댓글 접근 불가시 빈 리스트 반환
        return []


def extract_keywords_from_text(text: str, max_keywords: int = 10) -> List[str]:
    """텍스트에서 키워드 추출 (간단한 빈도 기반)."""
    import re
    from collections import Counter

    # 한글, 영어, 숫자만 추출
    words = re.findall(r"[가-힣a-zA-Z0-9]{2,}", text.lower())

    # 불용어 제거 (간단한 예시)
    stop_words = {
        "그래서",
        "그런데",
        "하지만",
        "그리고",
        "그러나",
        "그냥",
        "정말",
        "진짜",
        "완전",
        "the",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
    }

    filtered_words = [word for word in words if word not in stop_words and len(word) > 1]

    # 빈도 계산 및 상위 키워드 반환
    counter = Counter(filtered_words)
    return [word for word, count in counter.most_common(max_keywords)]


async def analyze_video_sentiment(title: str, description: str, comments: List[str]) -> str:
    """비디오의 전반적인 감정 분석 (간단한 규칙 기반)."""
    positive_words = ["좋", "최고", "대박", "멋지", "훌륭", "완벽", "사랑", "감사", "재밌", "웃기"]
    negative_words = ["싫", "별로", "최악", "나쁘", "화나", "짜증", "실망", "지루", "아쉽"]

    all_text = f"{title} {description} {' '.join(comments[:20])}"  # 상위 20개 댓글만 분석

    positive_count = sum(1 for word in positive_words if word in all_text)
    negative_count = sum(1 for word in negative_words if word in all_text)

    if positive_count > negative_count * 1.5:
        return "긍정적인 반응이 많은 스트림"
    elif negative_count > positive_count * 1.5:
        return "부정적인 반응이 있는 스트림"
    else:
        return "중립적인 반응의 스트림"


@router.post("/analyze-streams", response_model=StreamAnalysisResponse)
async def analyze_streams(request: StreamAnalysisRequest, settings: Settings = Depends(get_settings)):
    """YouTube 스트림들을 분석하여 상세 정보 제공."""
    if not settings.youtube_api_key:
        raise HTTPException(status_code=400, detail="YouTube API 키가 설정되지 않았습니다.")

    videos = []
    total_views = 0
    total_likes = 0
    total_comments = 0
    all_keywords = []

    for url in request.video_urls[:10]:  # 최대 10개 영상만 처리
        try:
            video_id = extract_video_id(url)

            # 비디오 상세 정보 가져오기
            video_data = await get_video_details(video_id, settings.youtube_api_key)
            snippet = video_data["snippet"]
            statistics = video_data["statistics"]
            content_details = video_data["contentDetails"]

            # 댓글 가져오기
            comments_data = []
            if request.extract_comments:
                comments_data = await get_video_comments(video_id, settings.youtube_api_key, request.max_comments)

            # 댓글 처리
            top_comments = []
            comment_texts = []
            for comment_item in comments_data:
                comment = comment_item["snippet"]["topLevelComment"]["snippet"]
                top_comments.append(
                    VideoComment(
                        author=comment["authorDisplayName"],
                        text=comment["textDisplay"][:200],  # 200자 제한
                        like_count=comment.get("likeCount", 0),
                        published_at=comment["publishedAt"],
                    )
                )
                comment_texts.append(comment["textDisplay"])

            # 키워드 추출
            text_for_keywords = f"{snippet['title']} {snippet.get('description', '')} {' '.join(comment_texts[:20])}"
            keywords = extract_keywords_from_text(text_for_keywords)
            all_keywords.extend(keywords)

            # 감정 분석
            sentiment = await analyze_video_sentiment(snippet["title"], snippet.get("description", ""), comment_texts)

            # 통계 정보
            video_stats = VideoStatistics(
                view_count=int(statistics.get("viewCount", 0)),
                like_count=int(statistics.get("likeCount", 0)),
                comment_count=int(statistics.get("commentCount", 0)),
                duration=content_details.get("duration", ""),
                published_at=snippet["publishedAt"],
            )

            # 전체 통계에 추가
            total_views += video_stats.view_count
            total_likes += video_stats.like_count
            total_comments += video_stats.comment_count

            # 비디오 분석 결과
            video_analysis = VideoAnalysis(
                video_id=video_id,
                title=snippet["title"],
                description=snippet.get("description", "")[:500],  # 500자 제한
                tags=snippet.get("tags", [])[:10],  # 최대 10개 태그
                statistics=video_stats,
                top_comments=top_comments[:10],  # 상위 10개 댓글
                extracted_keywords=keywords[:10],  # 상위 10개 키워드
                sentiment_summary=sentiment,
            )

            videos.append(video_analysis)

        except Exception as e:
            print(f"Error analyzing video {url}: {str(e)}")
            continue

    # 공통 키워드 추출
    from collections import Counter

    keyword_counter = Counter(all_keywords)
    common_keywords = [word for word, count in keyword_counter.most_common(15)]

    # 전체 요약 생성
    avg_views = total_views // len(videos) if videos else 0
    summary = f"총 {len(videos)}개 영상 분석 완료. 평균 조회수 {avg_views:,}회, 총 좋아요 {total_likes:,}개, 총 댓글 {total_comments:,}개"

    return StreamAnalysisResponse(
        videos=videos,
        summary=summary,
        common_keywords=common_keywords,
        total_engagement={
            "total_views": total_views,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "average_views": avg_views,
        },
    )


@router.post("/analyze-single-video")
async def analyze_single_video(video_url: str, settings: Settings = Depends(get_settings)):
    """단일 비디오 분석."""
    request = StreamAnalysisRequest(video_urls=[video_url])
    result = await analyze_streams(request, settings)

    if not result.videos:
        raise HTTPException(status_code=404, detail="비디오 분석에 실패했습니다.")

    return result.videos[0]


@router.get("/video-id/{video_url:path}")
async def extract_video_id_endpoint(video_url: str):
    """YouTube URL에서 비디오 ID 추출."""
    try:
        video_id = extract_video_id(video_url)
        return {"video_id": video_id, "url": video_url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
