"""LLM integration API endpoints."""

from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from uha.backend.container import ApplicationContainer
from uha.backend.database.models import DatabaseManager
from uha.backend.models.stream_models import (
    LiveStreamEntry,
    PaginatedStreamsRequest,
    PaginatedStreamsResponse,
    StreamWithDetails,
)
from uha.backend.services.cache_service import StreamCacheService
from uha.backend.settings import Settings

router = APIRouter(prefix="/llm", tags=["LLM"])

# Initialize database and cache service
db_manager = DatabaseManager()
cache_service = StreamCacheService(db_manager)


class SummaryRequest(BaseModel):
    content: str
    max_tokens: Optional[int] = 500
    temperature: Optional[float] = 0.7


class SummaryResponse(BaseModel):
    summary: str
    original_length: int
    summary_length: int


class LiveStreamSummaryRequest(BaseModel):
    year: int
    date_filter: Optional[str] = None  # YYYY-MM-DD format
    include_detailed_analysis: bool = False  # YouTube Data API 상세 분석 포함 여부
    max_videos_to_analyze: int = 20  # 분석할 최대 영상 수


class LiveStreamSummaryResponse(BaseModel):
    entries: List[LiveStreamEntry]
    summary: str
    total_streams: int
    detailed_analysis: Optional[Dict[str, Any]] = None  # YouTube Data API 분석 결과
    common_keywords: Optional[List[str]] = None  # 공통 키워드
    engagement_stats: Optional[Dict[str, int]] = None  # 참여도 통계


async def get_settings() -> Settings:
    """Get application settings."""
    container = ApplicationContainer()
    return container.settings.provided()


async def call_lm_studio(prompt: str, max_tokens: int = 500, temperature: float = 0.3) -> str:
    """Call LM Studio API for text generation."""
    url = "http://localhost:1234/v1/chat/completions"

    payload = {
        "model": "qwen/qwen3-4b",
        "messages": [
            {
                "role": "system",
                "content": "You must respond ONLY in Korean. 당신은 한국어 전문 분석가입니다. 반드시 한국어로만 답변하세요. 영어나 다른 언어는 절대 사용 금지입니다. 2-3문장으로 간결하게 요약해주세요.",
            },
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stop": ["\n\n", "요약:", "Summary:"],
    }

    try:
        print(f"LM Studio 호출 준비 중... URL: {url}")
        print(f"페이로드: {payload}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            print("HTTP 요청 시작...")
            response = await client.post(url, json=payload)
            print(f"응답 상태 코드: {response.status_code}")

        if response.status_code != 200:
            print(f"응답 내용: {response.text}")
            raise HTTPException(status_code=500, detail=f"LM Studio API 호출 실패: {response.status_code}")

        data = response.json()
        print(f"LM Studio 응답 데이터: {data}")
        content = data["choices"][0]["message"]["content"]

        # Clean up AI response - remove thinking tags and extra content
        content = content.strip()
        if content.startswith("<think>"):
            # Find the end of thinking section and extract only the actual response
            think_end = content.find("</think>")
            if think_end != -1:
                content = content[think_end + 8 :].strip()

        # Remove any remaining XML-like tags
        import re

        content = re.sub(r"<[^>]+>", "", content).strip()

        # Take only the first few sentences for summary
        sentences = content.split(".")
        if len(sentences) > 4:
            content = ". ".join(sentences[:4]) + "."

        return content

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="LM Studio API 응답 시간 초과")
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="LM Studio 서버에 연결할 수 없습니다. http://localhost:1234 가 실행 중인지 확인해주세요.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LM Studio API 오류: {str(e)}")


async def fetch_live_stream_data(year: int) -> str:
    """Fetch live stream data from GitHub repository."""
    url = f"https://raw.githubusercontent.com/eun2ce/uzuhama-live-link/main/readme-{year}.md"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)

        if response.status_code != 200:
            raise HTTPException(status_code=404, detail=f"{year}년 라이브 스트림 데이터를 찾을 수 없습니다.")

        return response.text

    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="GitHub 저장소에 연결할 수 없습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 가져오기 오류: {str(e)}")


def parse_live_stream_data(content: str, date_filter: Optional[str] = None) -> List[LiveStreamEntry]:
    """Parse live stream data from markdown content."""
    entries = []
    lines = content.strip().split("\n")

    for line in lines:
        line = line.strip()

        # Skip header lines and separators
        if line.startswith("|") and "Date" not in line and "---" not in line:
            # Parse markdown table format: | Date | URL |
            parts = [part.strip() for part in line.split("|") if part.strip()]
            if len(parts) >= 2:
                date = parts[0].strip()
                url_part = parts[1].strip()

                # Extract URL from markdown link format [text](url)
                if url_part.startswith("[") and "](" in url_part and url_part.endswith(")"):
                    url = url_part.split("](")[1][:-1]  # Extract URL from [text](url)
                else:
                    url = url_part

                # Apply date filter if provided
                if date_filter and not date.startswith(date_filter):
                    continue

                entries.append(LiveStreamEntry(date=date, url=url))

        # Also handle tab-separated format for backward compatibility
        elif "\t" in line:
            parts = line.split("\t")
            if len(parts) >= 2:
                date = parts[0].strip()
                url = parts[1].strip()

                # Apply date filter if provided
                if date_filter and not date.startswith(date_filter):
                    continue

                entries.append(LiveStreamEntry(date=date, url=url))

    return entries


def extract_video_id_from_url(url: str) -> str:
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

    return ""


async def get_stream_details(entry: LiveStreamEntry, settings: Settings) -> StreamWithDetails:
    """Get detailed information for a single stream with caching."""
    print(f"스트림 상세 정보 가져오기 시작: {entry.url}")
    video_id = extract_video_id_from_url(entry.url)
    print(f"추출된 비디오 ID: {video_id}")

    if not video_id:
        print(f"비디오 ID 없음: {entry.url}")
        return StreamWithDetails(
            date=entry.date,
            url=entry.url,
            video_id=video_id,
        )

    # Try to get from cache first
    cached_stream = await cache_service.get_cached_stream(video_id)
    if cached_stream:
        print(f"캐시에서 스트림 데이터 로드: {video_id}")
        return cached_stream

    print(f"캐시에 없음, 새로 처리: {video_id}")

    stream_details = StreamWithDetails(
        date=entry.date,
        url=entry.url,
        video_id=video_id,
    )

    print(
        f"YouTube API 키 상태: {bool(settings.youtube_api_key)} (길이: {len(settings.youtube_api_key) if settings.youtube_api_key else 0})"
    )

    if not settings.youtube_api_key:
        print("YouTube API 키 없음 - 더미 데이터로 테스트")
        # 더미 데이터로 AI 요약 테스트
        stream_details.title = f"테스트 라이브 스트림 - {entry.date}"
        # YouTube 썸네일 URL 패턴 사용
        stream_details.thumbnail = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        stream_details.ai_summary = await generate_stream_summary(
            stream_details.title,
            "테스트용 라이브 스트림입니다. 시청자들과 함께 즐거운 시간을 보냈습니다.",
            ["재밌어요!", "대박!", "다음에도 해주세요"],
            ["게임", "라이브"],
            ["스트리밍", "재미"],
        )
        stream_details.highlights = ["🎮 게임 스트리밍", "💬 시청자와 소통"]
        stream_details.sentiment = "긍정적인 반응이 많은 스트림"
        stream_details.engagement_score = 7.5
        stream_details.category = "🎮 게임"
        stream_details.view_count = 1500
        stream_details.like_count = 120
        stream_details.comment_count = 45
        stream_details.duration = "PT1H30M"

        # Cache the dummy data
        await cache_service.cache_stream(stream_details)
        return stream_details

    try:
        # YouTube Data API 호출
        from uha.backend.api.youtube_analysis import extract_keywords_from_text, get_video_comments, get_video_details

        video_data = await get_video_details(video_id, settings.youtube_api_key)
        snippet = video_data["snippet"]
        statistics = video_data["statistics"]
        content_details = video_data["contentDetails"]

        # 댓글 가져오기
        comments_data = await get_video_comments(video_id, settings.youtube_api_key, max_results=20)
        comment_texts = []
        for comment_item in comments_data:
            comment = comment_item["snippet"]["topLevelComment"]["snippet"]
            comment_texts.append(comment["textDisplay"])

        # 썸네일 URL
        thumbnails = snippet.get("thumbnails", {})
        thumbnail_url = (
            thumbnails.get("maxres", {}).get("url")
            or thumbnails.get("high", {}).get("url")
            or thumbnails.get("medium", {}).get("url")
            or thumbnails.get("default", {}).get("url")
        )

        # 키워드 추출
        text_for_keywords = f"{snippet['title']} {snippet.get('description', '')}"
        keywords = extract_keywords_from_text(text_for_keywords, max_keywords=5)

        # 기본 정보 설정
        stream_details.title = snippet["title"]
        stream_details.thumbnail = thumbnail_url
        stream_details.view_count = int(statistics.get("viewCount", 0))
        stream_details.like_count = int(statistics.get("likeCount", 0))
        stream_details.comment_count = int(statistics.get("commentCount", 0))
        stream_details.duration = content_details.get("duration", "")
        stream_details.tags = snippet.get("tags", [])[:5]  # 최대 5개 태그
        stream_details.keywords = keywords

        # 추가 분석 정보 생성
        try:
            print(f"AI 분석 시작: {video_id} - {snippet['title']}")
            # AI 요약 생성
            stream_details.ai_summary = await generate_stream_summary(
                snippet["title"], snippet.get("description", ""), comment_texts, stream_details.tags or [], keywords
            )
            print(f"AI 요약 완료: {stream_details.ai_summary[:50]}...")

            # 하이라이트 추출
            stream_details.highlights = extract_highlights_from_comments(comment_texts, snippet["title"])

            # 감정 분석
            from uha.backend.api.youtube_analysis import analyze_video_sentiment

            stream_details.sentiment = await analyze_video_sentiment(
                snippet["title"], snippet.get("description", ""), comment_texts
            )

            # 참여도 점수 계산
            duration_minutes = parse_duration_to_minutes(stream_details.duration)
            stream_details.engagement_score = calculate_engagement_score(
                stream_details.view_count, stream_details.like_count, stream_details.comment_count, duration_minutes
            )

            # 카테고리 분류
            stream_details.category = categorize_stream(snippet["title"], stream_details.tags or [], keywords)

        except Exception as analysis_error:
            print(f"Error in additional analysis for {video_id}: {str(analysis_error)}")
            # 기본값 설정
            stream_details.ai_summary = f"{snippet['title']}에서 진행된 라이브 스트리밍입니다."
            stream_details.highlights = ["📺 라이브 방송"]
            stream_details.sentiment = "중립적인 반응의 스트림"
            stream_details.engagement_score = 0.0
            stream_details.category = "📺 일반"

    except Exception as e:
        print(f"Error getting details for {entry.url}: {str(e)}")

    # Cache the processed stream data
    await cache_service.cache_stream(stream_details)
    return stream_details


async def generate_stream_summary(
    title: str, description: str, comments: List[str], tags: List[str], keywords: List[str]
) -> str:
    """개별 스트림에 대한 AI 요약 생성."""
    try:
        print(f"요약 생성 함수 호출: {title}")

        # 댓글에서 주요 내용 추출 (상위 10개)
        top_comments = comments[:10]
        comments_text = " ".join(top_comments) if top_comments else ""

        # 태그와 키워드 결합
        all_tags = ", ".join(tags + keywords) if tags or keywords else ""

        prompt = f"""
다음 라이브 스트림 정보를 바탕으로 한국어로 2-3문장의 간결한 요약을 작성해주세요:

제목: {title}
설명: {description[:200]}...
주요 태그/키워드: {all_tags}
시청자 댓글 요약: {comments_text[:300]}...

요약 조건:
1. 스트림의 주요 내용과 특징을 간결하게 설명
2. 시청자들의 반응이나 하이라이트가 있다면 포함
3. 한국어로만 작성, 2-3문장 이내
4. 구체적이고 흥미로운 내용 위주로 작성

요약:"""

        print("LM Studio 호출 시작...")
        summary = await call_lm_studio(prompt, max_tokens=200, temperature=0.4)
        print(f"LM Studio 응답: {summary}")

        # 요약이 너무 짧거나 영어인 경우 기본 요약 제공
        if (
            not summary
            or len(summary.strip()) < 10
            or any(word in summary for word in ["Let me", "Based on", "The stream"])
        ):
            summary = f"{title}에서 진행된 라이브 스트리밍입니다. "
            if tags:
                summary += f"주요 내용은 {', '.join(tags[:3])} 관련이며, "
            summary += "시청자들과의 실시간 소통이 활발했습니다."

        return summary.strip()

    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        return f"{title}에서 진행된 라이브 스트리밍입니다."


def extract_highlights_from_comments(comments: List[str], title: str) -> List[str]:
    """댓글에서 하이라이트 추출."""
    if not comments:
        return []

    highlights = []
    highlight_keywords = [
        "대박",
        "최고",
        "웃겨",
        "재밌",
        "감동",
        "놀라",
        "신기",
        "멋지",
        "완벽",
        "훌륭",
        "funny",
        "amazing",
        "great",
        "awesome",
        "perfect",
        "incredible",
        "wow",
    ]

    # 하이라이트 키워드가 포함된 댓글 찾기
    for comment in comments[:20]:  # 상위 20개 댓글만 확인
        comment_lower = comment.lower()
        if any(keyword in comment_lower for keyword in highlight_keywords):
            # 댓글을 간단히 정리해서 하이라이트로 추가
            clean_comment = comment.strip()[:50]  # 50자 제한
            if clean_comment and clean_comment not in highlights:
                highlights.append(clean_comment)
                if len(highlights) >= 3:  # 최대 3개
                    break

    # 하이라이트가 없으면 기본 하이라이트 생성
    if not highlights:
        if "게임" in title or "game" in title.lower():
            highlights.append("🎮 게임 스트리밍")
        if "채팅" in title or "chat" in title.lower():
            highlights.append("💬 시청자와 소통")
        if not highlights:
            highlights.append("📺 라이브 방송")

    return highlights


def calculate_engagement_score(view_count: int, like_count: int, comment_count: int, duration_minutes: int) -> float:
    """참여도 점수 계산."""
    if view_count == 0:
        return 0.0

    # 기본 참여도 계산 (좋아요율 + 댓글율)
    like_rate = (like_count / view_count) * 100
    comment_rate = (comment_count / view_count) * 100

    # 시간당 참여도 조정 (긴 스트림일수록 참여도가 높게 평가)
    duration_factor = min(duration_minutes / 60, 3)  # 최대 3시간까지만 보너스

    engagement_score = (like_rate * 0.6 + comment_rate * 0.4) * (1 + duration_factor * 0.1)

    return round(min(engagement_score, 10.0), 2)  # 최대 10점


def categorize_stream(title: str, tags: List[str], keywords: List[str]) -> str:
    """스트림 카테고리 분류."""
    all_text = f"{title} {' '.join(tags)} {' '.join(keywords)}".lower()

    categories = {
        "🎮 게임": ["게임", "game", "플레이", "play", "rpg", "fps", "moba"],
        "🎵 음악": ["음악", "music", "노래", "song", "sing", "cover"],
        "🗣️ 토크": ["토크", "talk", "채팅", "chat", "소통", "qa", "질문"],
        "🎨 창작": ["그림", "draw", "art", "창작", "만들기", "diy"],
        "📚 교육": ["강의", "교육", "tutorial", "배우기", "learn", "study"],
        "🍳 요리": ["요리", "cook", "먹방", "food", "recipe"],
        "🏃 운동": ["운동", "workout", "fitness", "헬스", "스포츠"],
        "🎬 리뷰": ["리뷰", "review", "후기", "평가", "반응"],
    }

    for category, category_keywords in categories.items():
        if any(keyword in all_text for keyword in category_keywords):
            return category

    return "📺 일반"


def parse_duration_to_minutes(duration: str) -> int:
    """ISO 8601 duration을 분 단위로 변환."""
    if not duration:
        return 0

    import re

    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration)
    if not match:
        return 0

    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0

    return hours * 60 + minutes + (seconds // 60)


async def analyze_stream_details(
    entries: List[LiveStreamEntry], settings: Settings, max_videos: int = 20
) -> Dict[str, Any]:
    """YouTube Data API를 활용한 스트림 상세 분석."""
    try:
        # YouTube 분석 API 임포트 (여기서 임포트하여 순환 참조 방지)
        from uha.backend.api.youtube_analysis import StreamAnalysisRequest, analyze_streams

        # 분석할 영상 URL 선택 (최신순으로)
        video_urls = [entry.url for entry in entries[:max_videos]]

        # YouTube 분석 요청
        analysis_request = StreamAnalysisRequest(video_urls=video_urls, extract_comments=True, max_comments=20)

        # 분석 실행
        analysis_result = await analyze_streams(analysis_request, settings)

        return {
            "videos": [video.dict() for video in analysis_result.videos],
            "summary": analysis_result.summary,
            "common_keywords": analysis_result.common_keywords,
            "total_engagement": analysis_result.total_engagement,
        }

    except Exception as e:
        print(f"YouTube 분석 중 오류: {str(e)}")
        return {"error": f"YouTube 분석 실패: {str(e)}", "videos": [], "common_keywords": [], "total_engagement": {}}


@router.post("/summarize", response_model=SummaryResponse)
async def summarize_text(request: SummaryRequest):
    """Summarize given text using LM Studio."""
    prompt = f"다음 텍스트를 2-3문장으로 간결하게 요약해주세요:\n\n{request.content}"

    summary = await call_lm_studio(prompt, request.max_tokens, request.temperature)

    return SummaryResponse(
        summary=summary.strip(), original_length=len(request.content), summary_length=len(summary.strip())
    )


@router.post("/summarize-live-streams", response_model=LiveStreamSummaryResponse)
async def summarize_live_streams(request: LiveStreamSummaryRequest):
    """Summarize live stream data for a specific year."""
    settings = await get_settings()

    # Fetch live stream data
    content = await fetch_live_stream_data(request.year)

    # Parse the data
    entries = parse_live_stream_data(content, request.date_filter)

    if not entries:
        raise HTTPException(status_code=404, detail=f"{request.year}년 라이브 스트림 데이터가 없습니다.")

    # YouTube 상세 분석 수행 (옵션)
    detailed_analysis = None
    common_keywords = None
    engagement_stats = None

    if request.include_detailed_analysis and settings.youtube_api_key:
        print(f"YouTube 상세 분석 시작: {min(len(entries), request.max_videos_to_analyze)}개 영상")
        detailed_analysis = await analyze_stream_details(entries, settings, request.max_videos_to_analyze)
        common_keywords = detailed_analysis.get("common_keywords", [])
        engagement_stats = detailed_analysis.get("total_engagement", {})

    # Create summary prompt
    dates_only = [entry.date for entry in entries[:20]]  # Limit to first 20 entries for analysis
    dates_text = ", ".join(dates_only)

    # 상세 분석 데이터가 있으면 프롬프트에 포함
    additional_info = ""
    if detailed_analysis and detailed_analysis.get("videos"):
        video_count = len(detailed_analysis["videos"])
        total_views = engagement_stats.get("total_views", 0)
        total_likes = engagement_stats.get("total_likes", 0)
        keywords_text = ", ".join(common_keywords[:10]) if common_keywords else ""

        additional_info = f"""

추가 분석 데이터:
- 분석된 영상 수: {video_count}개
- 총 조회수: {total_views:,}회
- 총 좋아요: {total_likes:,}개
- 주요 키워드: {keywords_text}
"""

    prompt = f"""
{request.year}년에 총 {len(entries)}회의 라이브 스트림이 진행되었습니다. 주요 날짜는 {dates_text} 등입니다.
{additional_info}

이 데이터를 바탕으로 다음을 한국어로 3-4문장으로 요약해주세요:
1. 월별 활동량과 패턴
2. 가장 활발했던 시기
3. 전체적인 스트리밍 특징
4. 시청자 반응 및 참여도 (데이터가 있는 경우)

답변은 한국어로만 작성하고 구체적인 수치를 포함해주세요.
"""

    try:
        summary = await call_lm_studio(prompt, max_tokens=500, temperature=0.3)

        # If the summary is in English or contains thinking patterns, provide a fallback
        if not summary or "Okay" in summary or "Let me" in summary or len(summary.strip()) < 10:
            # Provide a simple Korean summary based on the data
            total_count = len(entries)
            first_date = entries[0].date if entries else ""
            last_date = entries[-1].date if entries else ""

            base_summary = f"{request.year}년에 총 {total_count}회의 라이브 스트림이 진행되었습니다. 활동 기간은 {last_date}부터 {first_date}까지이며, 꾸준한 방송 활동을 보여주었습니다."

            if engagement_stats:
                avg_views = engagement_stats.get("average_views", 0)
                total_likes = engagement_stats.get("total_likes", 0)
                base_summary += (
                    f" 분석된 영상들의 평균 조회수는 {avg_views:,}회이며, 총 {total_likes:,}개의 좋아요를 받았습니다."
                )

            summary = base_summary

    except Exception:
        # Fallback summary if LM Studio fails
        total_count = len(entries)
        summary = f"{request.year}년에 총 {total_count}회의 라이브 스트림이 진행되었습니다. 지속적인 방송 활동을 통해 시청자들과 꾸준히 소통했습니다."

    return LiveStreamSummaryResponse(
        entries=entries,
        summary=summary.strip(),
        total_streams=len(entries),
        detailed_analysis=detailed_analysis,
        common_keywords=common_keywords,
        engagement_stats=engagement_stats,
    )


@router.post("/streams", response_model=PaginatedStreamsResponse)
async def get_paginated_streams(request: PaginatedStreamsRequest):
    """Get paginated live streams with detailed information."""
    settings = await get_settings()

    # Fetch live stream data
    content = await fetch_live_stream_data(request.year)

    # Parse the data
    entries = parse_live_stream_data(content)

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

    # Get detailed information for each stream
    streams_with_details = []
    print(
        f"상세 정보 처리 시작 - include_details: {request.include_details}, youtube_api_key 존재: {bool(settings.youtube_api_key)}"
    )

    if request.include_details:
        print(f"상세 정보 가져오기: {len(paginated_entries)}개 스트림")
        # 동시에 여러 스트림 처리 (최대 5개씩)
        import asyncio

        async def process_batch(batch_entries):
            tasks = [get_stream_details(entry, settings) for entry in batch_entries]
            return await asyncio.gather(*tasks, return_exceptions=True)

        # 5개씩 배치로 처리
        for i in range(0, len(paginated_entries), 5):
            batch = paginated_entries[i : i + 5]
            batch_results = await process_batch(batch)

            for result in batch_results:
                if not isinstance(result, Exception):
                    streams_with_details.append(result)
                else:
                    print(f"Error processing stream: {result}")
    else:
        print("상세 정보 없이 기본 정보만 처리")
        # 상세 정보 없이 기본 정보만
        for entry in paginated_entries:
            video_id = extract_video_id_from_url(entry.url)
            streams_with_details.append(StreamWithDetails(date=entry.date, url=entry.url, video_id=video_id))

    return PaginatedStreamsResponse(
        streams=streams_with_details,
        total_streams=total_streams,
        current_page=request.page,
        total_pages=total_pages,
        per_page=request.per_page,
    )


@router.get("/health")
async def check_lm_studio_health():
    """Check if LM Studio is running and accessible."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:1234/v1/models")

        if response.status_code == 200:
            return {"status": "healthy", "message": "LM Studio is running"}
        else:
            return {"status": "unhealthy", "message": f"LM Studio returned status {response.status_code}"}

    except httpx.ConnectError:
        return {"status": "unhealthy", "message": "Cannot connect to LM Studio"}
    except Exception as e:
        return {"status": "unhealthy", "message": f"Error: {str(e)}"}


@router.post("/cache/clear")
async def clear_cache() -> dict:
    """Clear expired cache entries."""
    try:
        deleted_count = await cache_service.clear_expired_cache()
        return {"status": "success", "message": f"Cleared {deleted_count} expired cache entries"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to clear cache: {str(e)}"}


@router.get("/cache/stats")
async def cache_stats() -> dict:
    """Get cache statistics."""
    try:
        # Get cache statistics for recent years
        stats = {}
        for year in [2020, 2021, 2022, 2023, 2024, 2025]:
            count = await cache_service.get_cached_stream_count(year)
            if count > 0:
                stats[str(year)] = count

        return {"status": "success", "cached_streams_by_year": stats, "total_cached_streams": sum(stats.values())}
    except Exception as e:
        return {"status": "error", "message": f"Failed to get cache stats: {str(e)}"}
