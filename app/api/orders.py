from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from authx import TokenPayload
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from app.auth import auth
from app.domain.models import OrderStatus
from app.containers import Container
from app.services import OrderService


router = APIRouter()


class CreateOrderSchema(BaseModel):
    """ Заказ """

    items: Dict[str, Any]
    """ Список товаров """

    total_price: float
    """ Сумма """


class ResponseOrderSchema(BaseModel):
    """ Представление заказа в ответах API """

    id: UUID
    """ ID """

    items: Dict[str, Any]
    """ Список товаров """

    total_price: float
    """ Сумма """

    status: OrderStatus
    """ Статус заказа """

    created_at: datetime
    """ Дата создания (по Гринвичу) """


class ResponseOrdersSchema(BaseModel):
    """ Представление списка заказов в ответах API """

    orders: list[ResponseOrderSchema]
    """ Заказы """


@router.post(
    path='/',
    status_code=status.HTTP_201_CREATED,
    summary="Создать заказ"
)
@inject
async def create_order(
    data: CreateOrderSchema,
    token_payload: TokenPayload = Depends(auth.access_token_required),
    order_service: OrderService = Depends(Provide[Container.order_service])
):
    user_id = UUID(getattr(token_payload, 'sub'))
    new_order = await order_service.create(
        user_id=user_id, **data.model_dump()
    )
    return ResponseOrderSchema(**new_order.model_dump())


@router.get(
    path='/{order_id}',
    status_code=status.HTTP_200_OK,
    summary="Данные заказа"
)
@inject
async def get_order(
    order_id: UUID,
    order_service: OrderService = Depends(Provide[Container.order_service])
):
    order = await order_service.get(order_id)
    return ResponseOrderSchema(**order.model_dump())


@router.patch(
    path='/{order_id}',
    status_code=status.HTTP_202_ACCEPTED,
    summary="Обновить статус"
)
@inject
async def update_status(
    order_id: UUID,
    status: OrderStatus,
    order_service: OrderService = Depends(Provide[Container.order_service])
):
    order = await order_service.update_status(order_id, status)
    return ResponseOrderSchema(**order.model_dump())


@router.get(
    path='/user/{user_id}',
    status_code=status.HTTP_200_OK,
    summary="Заказы пользователя"
)
@inject
async def user_orders(
    user_id: UUID,
    order_service: OrderService = Depends(Provide[Container.order_service])
):
    orders = await order_service.get_for_user(user_id)
    return ResponseOrdersSchema(
        orders=[
            ResponseOrderSchema(**order.model_dump())
            for order in orders
        ]
    )
