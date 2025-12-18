from time import sleep
from uuid import UUID

from celery import Celery
from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """ Параметры Celery """

    # Реквизиты для подключения к Redis
    REDIS_HOST: str = Field(default='redis')
    REDIS_PORT: int = Field(default=6379)


config = Config()


sleep(15)  # Искуственная задержка до запуска RabbitMQ
app = Celery(
    'celery_app.main',
    broker=f'redis://{config.REDIS_HOST}:{config.REDIS_PORT}',
    backend="rpc://"
)


@app.task
def process_order(order_id: UUID):
    sleep(2)
    print(f"Order with id <{order_id}> processed")
