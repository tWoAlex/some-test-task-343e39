from uuid import UUID

from app.domain.models import Order as DomainOrder, OrderStatus
from app.storage.repos import OrderRepository


class OrderService:
    """ Сервис управления заказами """

    def __init__(self, repo: OrderRepository):
        self._repo = repo

    async def create(
        self,
        user_id: UUID,
        items: dict,
        total_price: float
    ) -> DomainOrder:
        """ Создать заказ """

        return await self._repo.put(
            DomainOrder(
                user_id=user_id,
                items=items,
                total_price=total_price
            )
        )

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
