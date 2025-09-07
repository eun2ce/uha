from pydantic_settings import BaseSettings, SettingsConfigDict

from uha.shared_kernel.domain.enum import ApplicationMode
from uha.shared_kernel.infra.database.sqla.settings import DatabaseSettings
from uha.shared_kernel.infra.settings.model import (
    CacheSettings,
    CORSSettings,
    FastAPISettings,
    GZipSettings,
    SessionSettings,
)


class Settings(BaseSettings):
    """Application settings."""

    mode: ApplicationMode = ApplicationMode.DEVELOPMENT
    db: DatabaseSettings = DatabaseSettings()
    cors: CORSSettings = CORSSettings(
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:8000",
            "http://localhost:8081",
            "http://127.0.0.1:8081",
        ]
    )
    gzip: GZipSettings = GZipSettings()
    cache: CacheSettings = CacheSettings()
    fastapi: FastAPISettings = FastAPISettings(
        title="uha API",
        description="A modern FastAPI project with clean architecture",
        docs_url="/docs",
        openapi_url="/openapi.json",
        redoc_url="/redoc",
    )
    session: SessionSettings = SessionSettings()

    # YouTube API settings
    youtube_api_key: str = ""
    youtube_channel_id: str = ""

    # Naver Cafe settings
    naver_cafe_id: str = ""

    # LM Studio settings
    lm_studio_url: str = "http://localhost:1234"

    model_config = SettingsConfigDict(
        env_prefix="UHA_", env_nested_delimiter="__", env_file=".env", env_file_encoding="utf-8", extra="allow"
    )


Settings.model_rebuild()
