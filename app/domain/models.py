from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Dict
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


class OrderStatus(StrEnum):
    CANCELLED = 'CANCELLED'
    PAID = 'PAID'
    PENDING = 'PENDING'
    SHIPPED = 'SHIPPED'


class Order(BaseModel):
    """ Заказ """

    id: UUID = Field(default_factory=uuid7)
    """ ID """

    user_id: UUID
    """ ID пользователя """

    items: Dict[str, Any]
    """ Список товаров """

    total_price: float
    """ Сумма """

    status: OrderStatus = OrderStatus.PENDING
    """ Статус заказа """

    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc).replace(tzinfo=None))
    """ Дата создания (по Гринвичу) """
