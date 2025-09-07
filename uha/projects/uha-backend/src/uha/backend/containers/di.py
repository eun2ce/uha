"""Dependency injection container."""

from dependency_injector import containers, providers

from ..services.ai_service import AIService, AIServiceConfig
from ..services.naver_cafe_service import NaverCafeService, NaverCafeServiceConfig
from ..services.stream_service import StreamService, StreamServiceConfig
from ..services.youtube_service import YouTubeService, YouTubeServiceConfig
from ..settings import Settings


class Container(containers.DeclarativeContainer):
    """Main DI container."""

    # Settings
    settings = providers.Singleton(Settings)

    # Service configurations
    ai_config = providers.Factory(
        AIServiceConfig,
        lm_studio_url=settings.provided.lm_studio_url,
        model_name="qwen/qwen3-4b",
        temperature=0.4,
        max_tokens=500,
        timeout_seconds=30,
    )

    youtube_config = providers.Factory(
        YouTubeServiceConfig,
        api_key=settings.provided.youtube_api_key,
        timeout_seconds=30,
        max_results_per_request=50,
    )

    naver_cafe_config = providers.Factory(
        NaverCafeServiceConfig,
        cafe_id=settings.provided.naver_cafe_id,
        timeout_seconds=30,
    )

    stream_config = providers.Factory(
        StreamServiceConfig,
        max_concurrent_analysis=5,
    )

    # Services
    ai_service = providers.Singleton(AIService, config=ai_config)
    youtube_service = providers.Singleton(YouTubeService, config=youtube_config)
    naver_cafe_service = providers.Singleton(NaverCafeService, config=naver_cafe_config)
    stream_service = providers.Singleton(
        StreamService,
        config=stream_config,
        ai_service=ai_service,
        youtube_service=youtube_service,
    )
