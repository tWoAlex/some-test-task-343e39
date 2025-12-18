from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSON as pgJSON, ENUM as pgENUM

from app.domain.models import OrderStatus


class Base(DeclarativeBase):
    """ Базовая модель """

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class User(Base):
    """ Пользователь """

    id: Mapped[UUID] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column()
    orders: Mapped[List['Order']] = relationship('Order', back_populates='user')


class Order(Base):
    """ Заказ """

    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey(User.id))
    user: Mapped['User'] = relationship('User', back_populates='orders')
    items: Mapped[dict] = mapped_column(pgJSON)
    total_price: Mapped[float] = mapped_column()
    status: Mapped[OrderStatus] = mapped_column(pgENUM(OrderStatus, name='order_status'))
    created_at: Mapped[datetime] = mapped_column()
