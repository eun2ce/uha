from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from uha.backend.api import llm, naver_cafe, youtube, youtube_analysis
from uha.backend.container import ApplicationContainer
from uha.backend.containers.di import Container
from uha.backend.database.models import DatabaseManager
from uha.backend.rest import ai_router, legacy_llm_controller, naver_cafe_router, stream_router, youtube_router
from uha.backend.settings import Settings
from uha.shared_kernel.domain.exception import BaseMsgException
from uha.shared_kernel.infra.fastapi.exception_handlers.base import custom_exception_handler
from uha.shared_kernel.infra.fastapi.middlewares.correlation_id import CorrelationIdMiddleware
from uha.shared_kernel.infra.fastapi.middlewares.session import SessionMiddleware
from uha.shared_kernel.infra.fastapi.utils.responses import MsgSpecJSONResponse

container = ApplicationContainer()
settings: Settings = container.settings.provided()

# New DI container
di_container = Container()
di_container.wire(
    modules=[
        "uha.backend.rest.stream_controller",
        "uha.backend.rest.youtube_controller",
        "uha.backend.rest.naver_cafe_controller",
        "uha.backend.rest.ai_controller",
        "uha.backend.rest.legacy_llm_controller",
    ]
)


async def init_database():
    """Initialize database tables."""
    db_manager = DatabaseManager()
    await db_manager.create_tables()
    await db_manager.close()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    middleware = [
        Middleware(CorrelationIdMiddleware),
        Middleware(
            CORSMiddleware,
            allow_origins=settings.cors.allow_origins,
            allow_credentials=settings.cors.allow_credentials,
            allow_methods=settings.cors.allow_methods,
            allow_headers=settings.cors.allow_headers,
        ),
        Middleware(SessionMiddleware, secret_key=settings.session.secret_key),
        Middleware(GZipMiddleware),
    ]

    app = FastAPI(
        title=settings.fastapi.title,
        description=settings.fastapi.description,
        contact=settings.fastapi.contact,
        summary=settings.fastapi.summary,
        middleware=middleware,
        docs_url=settings.fastapi.docs_url,
        redoc_url=settings.fastapi.redoc_url,
        openapi_url=settings.fastapi.openapi_url,
        default_response_class=MsgSpecJSONResponse,
        exception_handlers={
            BaseMsgException: custom_exception_handler,
        },
    )

    app.container = container  # type: ignore
    app.settings = settings  # type: ignore
    app.di_container = di_container  # type: ignore

    # Initialize database on startup
    @app.on_event("startup")
    async def startup_event():
        await init_database()

    # Include legacy routers for backward compatibility
    app.include_router(youtube.router)
    app.include_router(naver_cafe.router)
    app.include_router(llm.router)
    app.include_router(youtube_analysis.router)

    # Include new structured routers
    app.include_router(stream_router, prefix="/api/v1")
    app.include_router(youtube_router, prefix="/api/v1")
    app.include_router(naver_cafe_router, prefix="/api/v1")
    app.include_router(ai_router, prefix="/api/v1")
    app.include_router(legacy_llm_controller.router)

    # Add health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "ok", "message": "uha is running"}

    return app


app = create_app()
