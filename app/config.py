from pydantic import HttpUrl
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """ Параметры приложения """

    JWT_SECRET_KEY: str
    """ Секрет для генерации JWT-подписей """

    # Реквизиты для подключения к БД
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB_NAME: str
    POSTGRES_USERNAME: str
    POSTGRES_PWD: str

    # Реквизиты для подключения к Redis
    REDIS_HOST: str
    REDIS_PORT: int

    # Реквизиты для подключения к RabbitMQ
    RABBITMQ_USER: str
    RABBITMQ_PWD: str
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int

    # Кэш
    ORDER_CACHE_TTL: int = 300

    # Rate limit
    REQUESTS_PER_MINUTE_FOR_IP: int = 5

    # CORS
    CORS_ALLOWED_ORIGINS: list[HttpUrl]


config = Config()
