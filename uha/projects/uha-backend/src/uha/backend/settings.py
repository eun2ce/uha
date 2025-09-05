from pydantic_settings import BaseSettings, SettingsConfigDict

from uha.shared_kernel.domain.enum import ApplicationMode
from uha.shared_kernel.infra.settings.model import (
    SessionSettings,
    CacheSettings,
    CORSSettings,
    FastAPISettings,
    GZipSettings,
)
from uha.shared_kernel.infra.database.sqla.settings import DatabaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    mode: ApplicationMode = ApplicationMode.DEVELOPMENT
    db: DatabaseSettings = DatabaseSettings()
    cors: CORSSettings = CORSSettings()
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

    model_config = SettingsConfigDict(
        env_prefix="UHA_", 
        env_nested_delimiter="__", 
        env_file_encoding="utf-8", 
        extra="allow"
    )


Settings.model_rebuild()
