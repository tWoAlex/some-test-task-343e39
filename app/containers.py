import asyncio

from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import Coroutine, Factory, Object, Resource, Singleton

import aio_pika

from redis.asyncio import Redis as AsyncRedis

from sqlalchemy.engine import URL as DB_URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.config import config
from app.events.bus import EventBus
from app.services import OrderService, UserService
from app.storage.models import Base
from app.storage.repos import OrderRepository, UserRepository


async def create_rabbitmq_connection() -> aio_pika.abc.AbstractConnection:
    await asyncio.sleep(15)
    return await aio_pika.connect(
        host=config.RABBITMQ_HOST,
        port=config.RABBITMQ_PORT,
        login=config.RABBITMQ_USER,
        password=config.RABBITMQ_PWD,
    )


async def create_rabbitmq_channel(connection: aio_pika.abc.AbstractConnection):
    """ Создать канал внутри подключения к RabbitMQ """

    return await connection.channel()


class Container(DeclarativeContainer):
    """ Контейнер с зависимостями """

    wiring_config = WiringConfiguration(modules=(
        'app.api.orders',
        'app.api.users',
        'app.main',
    ))

    # Подключение к БД
    db_url = Singleton(
        DB_URL.create,
        drivername='postgresql+asyncpg',
        host=config.POSTGRES_HOST,
        port=config.POSTGRES_PORT,
        username=config.POSTGRES_USER,
        password=config.POSTGRES_PASSWORD,
        database=config.POSTGRES_DB_NAME
    )
    db_metadata = Object(Base.metadata)
    db_engine = Resource(create_async_engine, url=db_url)
    db_session = Factory(AsyncSession, bind=db_engine, expire_on_commit=False)

    # Клиент Redis
    redis_client = Singleton(AsyncRedis, host=config.REDIS_HOST, port=config.REDIS_PORT)

    # Подключение к RabbitMQ
    rabbitmq_connection = Resource(create_rabbitmq_connection)
    rabbitmq_channel = Coroutine(create_rabbitmq_channel, connection=rabbitmq_connection)

    # Репозитории
    user_repo = Factory(UserRepository, session=db_session)
    order_repo = Factory(OrderRepository, session=db_session, redis_client=redis_client)

    # Шина сообщений
    event_bus = Factory(EventBus, channel=rabbitmq_channel)

    # Сервисы
    user_service = Factory(UserService, repo=user_repo)
    order_service = Factory(OrderService, repo=order_repo, event_bus=event_bus)
