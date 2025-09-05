from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from uha.shared_kernel.infra.database.sqla.settings import DatabaseSettings


class SqlaContainer(containers.DeclarativeContainer):
    """SQLAlchemy dependency injection container."""
    
    settings = providers.Dependency(instance_of=DatabaseSettings)
    
    engine = providers.Singleton(
        create_async_engine,
        url=settings.provided.url,
        echo=settings.provided.echo,
        pool_size=settings.provided.pool_size,
        max_overflow=settings.provided.max_overflow,
        pool_recycle=settings.provided.pool_recycle,
        pool_timeout=settings.provided.pool_timeout,
        pool_pre_ping=settings.provided.pool_pre_ping,
    )
    
    session_factory = providers.Singleton(
        sessionmaker,
        bind=engine.provided,
        class_=AsyncSession,
        expire_on_commit=False,
    )
