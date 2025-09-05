from pydantic import BaseModel, Field


class DatabaseSettings(BaseModel):
    """Database configuration settings."""

    url: str = Field("sqlite+aiosqlite:///./data/database.db", description="Database URL")
    echo: bool = Field(False, description="Echo SQL queries")
    pool_size: int = Field(10, description="Connection pool size")
    max_overflow: int = Field(2, description="Max overflow connections")
    pool_recycle: int = Field(3600, description="Pool recycle time in seconds")
    pool_timeout: int = Field(30, description="Pool timeout in seconds")
    pool_pre_ping: bool = Field(True, description="Enable pool pre-ping")
