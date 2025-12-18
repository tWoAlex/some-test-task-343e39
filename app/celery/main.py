from time import sleep
from uuid import UUID

from celery import Celery
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """ Параметры Celery """

    # Реквизиты для подключения к Redis
    REDIS_HOST: str
    REDIS_PORT: int


config = Config()


app = Celery(
    'celery_app.main',
    broker=f'redis://{config.REDIS_HOST}:{config.REDIS_PORT}',
    backend="rpc://"
)


@app.task
def process_order(order_id: UUID):
    sleep(2)
    print(f"Order with id <{order_id}> processed")
