from uuid import UUID, uuid7

from pydantic import BaseModel, Field


class User(BaseModel):
    """ Пользователь """

    id: UUID = Field(default_factory=uuid7)
    """ ID """

    email: str
    """ Email """

    hashed_password: str
    """ Хешированный пароль """
