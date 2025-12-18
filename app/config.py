from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """ Параметры приложения """

    JWT_SECRET_KEY: str
    """ Секрет для генерации JWT-подписей """

    # Реквизиты для подключения к БД
    POSTGRES_HOST: str = Field(default='postgres')
    POSTGRES_PORT: int = Field(default=5432)
    POSTGRES_DB_NAME: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    # Реквизиты для подключения к Redis
    REDIS_HOST: str = Field(default='redis')
    REDIS_PORT: int = Field(default=6379)

    # Реквизиты для подключения к RabbitMQ
    RABBITMQ_USER: str = Field(alias='RABBITMQ_DEFAULT_USER')
    RABBITMQ_PWD: str = Field(alias='RABBITMQ_DEFAULT_PASS')
    RABBITMQ_HOST: str = Field(default='rabbitmq')
    RABBITMQ_PORT: int = Field(default=5672)

    # Кэш
    ORDER_CACHE_TTL: int = 300

    # Rate limit
    REQUESTS_PER_MINUTE_FOR_IP: int

    # CORS
    CORS_ALLOWED_ORIGINS: list[HttpUrl]

    # Настройки Consumer'а
    CONSUMER_PREFETCH_LIMIT: int


config = Config()
