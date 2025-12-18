from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import Order as DomainOrder, User as DomainUser
from .models import Order as DBOrder, User as DBUser


class UserRepository:
    """ Репозиторий пользователей """

    def __init__(self, session: AsyncSession):
        self._session = session

    def _db_to_domain_model(self, from_db: DBUser):
        """ Превратить модель из БД в доменную """

        return DomainUser(
            **{
                key: getattr(from_db, key)
                for key in DomainUser.model_fields.keys()
            }
        )

    async def add(self, user: DomainUser) -> DomainUser:
        """
        Добавить/обновить пользователя

        :raises ValueError: Пользователь уже есть в базе
        """

        query = insert(DBUser).values(**user.model_dump()).returning(DBUser)
        async with self._session.begin():
            try:
                from_db = await self._session.scalar(query)
            except IntegrityError:
                raise ValueError("User already exists")
        return self._db_to_domain_model(from_db)

    async def get_by_email(self, email: str) -> DomainUser | None:
        """ Получить пользователя по email """

        query = select(DBUser).where(DBUser.email == email)
        async with self._session.begin():
            from_db = await self._session.scalar(query)
        if from_db:
            return self._db_to_domain_model(from_db)


class OrderRepository:
    """ Репозиторий заказов """

    def __init__(self, session: AsyncSession):
        self._session = session

    def _db_to_domain_model(self, from_db: DBOrder):
        """ Превратить модель из БД в доменную """

        return DomainOrder(
            id=from_db.id,
            user_id=from_db.user_id,
            items=from_db.items,
            total_price=from_db.total_price,
            status=from_db.status,
            created_at=from_db.created_at
        )

    async def put(self, order: DomainOrder) -> DomainOrder:
        """ Добавить/обновить заказ """

        data = order.model_dump()
        id = data.pop('id')

        query = (
            insert(DBOrder)
            .values(id=id, **data)
            .on_conflict_do_update(constraint=DBOrder.__table__.primary_key, set_=data)
            .returning(DBOrder)
        )
        async with self._session.begin():
            from_db = await self._session.scalar(query)
        return self._db_to_domain_model(from_db)

    async def get(self, order_id: UUID) -> DomainOrder | None:
        """ Заказ по ID """

        query = select(DBOrder).where(DBOrder.id == order_id)
        async with self._session.begin():
            from_db = await self._session.scalar(query)
        if from_db is not None:
            return self._db_to_domain_model(from_db)

    async def get_for_user(self, user_id: UUID) -> list[DomainOrder]:
        """ Заказы пользователя """

        query = select(DBOrder).where(DBOrder.user_id == user_id)
        async with self._session.begin():
            from_db = await self._session.scalars(query)
        return [self._db_to_domain_model(order) for order in from_db]
