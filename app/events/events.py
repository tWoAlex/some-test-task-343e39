from abc import ABC
from typing import ClassVar

from pydantic import BaseModel

from app.domain.models import Order as DomainOrder


class AbstractEvent(BaseModel, ABC):
    """ Абстрактное событие """

    routing_key: ClassVar[str] = 'new_abstract_event'


class NewOrder(AbstractEvent):
    """ Создан заказ """

    routing_key: ClassVar[str] = 'new_order'
    order_data: DomainOrder
