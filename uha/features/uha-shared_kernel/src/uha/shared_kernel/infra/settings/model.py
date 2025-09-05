import typing as T
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class DatabaseSettings(BaseModel):
    url: str = Field("", description="Database URL", init=False)
    init: bool = False
    echo: bool = True
    pool_size: int = 10
    max_overflow: int = 2
    pool_recycle: int = 3600
    pg_schema: str = "public"
    pool_timeout: int = 30
    pool_pre_ping: bool = True

    def dict(self):
        return {
            "url": self.url,
            "echo": self.echo,
            "max_overflow": self.max_overflow,
        }


class AWSSettings(BaseModel):
    region: str = "us-east-1"
    endpoint_url: str | None = None


class LoggerSettings(BaseModel):
    path: str = "logs"
    filename: str = "access.json"
    level: str = "info"
    rotation: str = "1 days"
    retention: str = "1 months"


class CacheSettings(BaseModel):
    backend_url: str | None = None
    expire: int = 30
    prefix: str = ""
    enable: bool = True


class JWTSettings(BaseModel):
    secret_key: str = "your-jwt-secret-key-here"
    algorithm: str = "HS256"
    refresh_token_exp: int = 31_536_000
    access_token_exp: int = 31_536_000


class AuthManagerSettings(BaseModel):
    secret_key: str = "your-auth-manager-secret-key"
    lifetime_seconds: int = 300


class OAuthSettings(BaseModel):
    client_id: str = ""
    client_secrets: str = ""
    redirect_url: str | None = None


class AuthSettings(BaseModel):
    cookie_max_age: int = 3600
    cookie_name: str = "x-auth-session"
    cookie_domain: str | None = None
    state_secret: str = "your-state-secret"


class GZipSettings(BaseModel):
    enable: bool = True
    minimum_size: int = 800
    compress_level: int = 9

    @field_validator("compress_level")
    def check_compress_level_rate(cls, v):
        if not (0 <= v <= 9):
            raise ValueError(f"GZIP_COMPRESS_LEVEL Range ERR,{v} is not in 0~9")
        return v


class CORSSettings(BaseModel):
    allow_origins: T.List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    allow_credentials: bool = True
    allow_methods: T.List[str] = ["*"]
    allow_headers: T.List[str] = ["*"]


class SessionSettings(BaseModel):
    secret_key: str = "your-session-secret-key"


class RedisStoreSettings(BaseModel):
    url: str = ""
    lifetime_seconds: int = 31536000


class AuthCookieSettings(BaseModel):
    name: str = "x-auth-cookie"
    domain: str | None = None
    samesite: T.Literal["lax", "strict", "none"] = "none"


class EmailSettings(BaseModel):
    sender: str = "no-reply@example.com"
    domain_url: str = "https://example.com"
    reset_password_path: str = "reset-password"
    invite_path: str = "auth/callback/org/invite"
    verify_path: str = "auth/callback/verify"


class RatelimiterSettings(BaseModel):
    key_func: str = "get_remote_address"
    key_prefix: str = ""
    enabled: bool = True
    storage_uri: str | None = None
    strategy: str = "moving-window"


class ObjectStorageSettings(BaseModel):
    bucket: str = "your-bucket-name"
    prefix_key: str | None = None


class SentrySettings(BaseModel):
    dsn: str = ""
    traces_sample_rate: float = 1.0
    profiles_sample_rate: float = 1.0
    environment: str = "development"


class CookieSettings(BaseModel):
    key: str = ""
    domain: str | None = None
    samesite: T.Literal["lax", "strict", "none"] = "lax"
    httponly: bool = True
    path: str = "/"
    secure: bool = True
    max_age: int | None = None
    expires: datetime | str | int | None = None


class FastAPISettings(BaseModel):
    title: str = "uha API"
    description: str = "A modern FastAPI project with clean architecture"
    docs_url: str | None = None
    redoc_url: str | None = None
    openapi_url: str = "/openapi.json"
    contact: dict = {
        "name": "eun2ce",
        "email": "joeun2ce@gmail.com",
    }
    summary: str = "uha API"


class RedisSettings(BaseModel):
    url: str = ""


class RabbitMqSettings(BaseModel):
    url: str = Field(default="amqp://guest:guest@localhost:5672/")
    virtualhost: str = Field(default="/")
    pool_max: int = Field(default=10)
    pool_min: int = Field(default=2)


class S3UploadSettings(BaseModel):
    bucket_name: str = "your-bucket-name"
    dir_name: str = "uploads"
    cdn_url: str = "https://cdn.example.com"


class PrometheusSettings(BaseModel):
    secret: str = "your-prometheus-secret"
    should_gzip: bool = True
    endpoint: str = "/metrics"
    include_in_schema: bool = False
    namespace: str = "uha"
    metric_subsystem: str = ""


class OpenAISettings(BaseModel):
    api_key: str = ""
