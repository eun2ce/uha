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
        modules=[],
    )

    settings = providers.Resource(Settings)  # type: ignore
    database = providers.Container(SqlaContainer, settings=settings.provided.db)
    async_http_client = providers.Singleton(http_client)
