from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import Factory, Object, Singleton

from sqlalchemy.engine import URL as DB_URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.config import config
from app.storage.models import Base
from app.storage.repos import UserRepository
from app.services import UserService


class Container(DeclarativeContainer):
    """ Контейнер с зависимостями """

    wiring_config = WiringConfiguration(modules=(
        'app.api.users',
    ))

    # Подключение к БД
    db_url = Singleton(
        DB_URL.create,
        drivername='postgresql+asyncpg',
        host=config.POSTGRES_HOST,
        port=config.POSTGRES_PORT,
        username=config.POSTGRES_USERNAME,
        password=config.POSTGRES_PWD,
        database=config.POSTGRES_DB_NAME
    )
    db_metadata = Object(Base.metadata)
    db_engine = Singleton(create_async_engine, url=db_url)
    db_session = Factory(AsyncSession, bind=db_engine, expire_on_commit=False)

    # Репозитории
    user_repo = Factory(UserRepository, session=db_session)

    # Сервисы
    user_service = Factory(UserService, repo=user_repo)
