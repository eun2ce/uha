import boto3.session
import httpx
from dependency_injector import containers, providers

from uha.backend.settings import Settings
from uha.shared_kernel.infra.database.sqla.container.di import SqlaContainer


def http_client(retries: int = 3):
    """Create an async HTTP client with retry configuration."""
    transports = httpx.AsyncHTTPTransport(retries=retries)
    client = httpx.AsyncClient(transport=transports)
    return client


class ApplicationContainer(containers.DeclarativeContainer):
    """Main application container for dependency injection."""
    
    wiring_config = containers.WiringConfiguration(
        packages=[],
        modules=[
            "uha.shared_kernel.infra.object_storage.s3",
            "uha.shared_kernel.infra.database.sqla.mixin",
        ],
    )

    settings = providers.Resource(Settings)  # type: ignore
    boto_session = providers.Resource(boto3.session.Session, region_name="us-east-1")
    s3_client = providers.Resource(
        providers.MethodCaller(boto_session.provided.client),
        service_name="s3",
    )
    sns_client = providers.Resource(
        providers.MethodCaller(boto_session.provided.client),
        service_name="sns",
    )
    database = providers.Container(SqlaContainer, settings=settings.provided.db)

    async_http_client = providers.Singleton(http_client)
