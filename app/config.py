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


config = Config()
