from uuid import UUID

from app.events.bus import EventBus
from app.events.events import NewOrder as NewOrderEvent
from app.domain.models import Order as DomainOrder, OrderStatus
from app.storage.repos import OrderRepository


class OrderService:
    """ Сервис управления заказами """

    def __init__(self, repo: OrderRepository, event_bus: EventBus):
        self._repo = repo
        self._event_bus = event_bus

    async def create(
        self,
        user_id: UUID,
        items: dict,
        total_price: float
    ) -> DomainOrder:
        """ Создать заказ """

        new_order = await self._repo.put(
            DomainOrder(
                user_id=user_id,
                items=items,
                total_price=total_price
            )
        )
        await self._event_bus.publish(
            NewOrderEvent(order_data=new_order)
        )
        return new_order

    async def get(self, order_id: UUID) -> DomainOrder:
        """
        Заказ по ID

        :raises KeyError: Заказ не существует
        """

        order = await self._repo.get(order_id)
        if order is None:
            raise KeyError("Order does not exist")
        return order

    async def update_status(self, order_id: UUID, new_status: OrderStatus) -> DomainOrder:
        """
        Обновить статус заказа

        :raises KeyError: Заказ не существует
        """

        order = await self._repo.get(order_id)
        if order is None:
            raise KeyError("Order does not exist")

        order.status = new_status
        return await self._repo.put(order)

    async def get_for_user(self, user_id: UUID) -> list[DomainOrder]:
        """ Заказы пользователя """

        return await self._repo.get_for_user(user_id)
