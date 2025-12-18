from datetime import datetime, timezone
from uuid import UUID

from redis.asyncio import Redis as AsyncRedis

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import Order as DomainOrder, User as DomainUser
from .models import Order as DBOrder, User as DBUser

from app.config import config


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

    CACHE_ORDER_LAST_REQUEST_KEY_TEMPLATE = 'order_request:<{order_id}>'
    CACHE_ORDER_KEY_TEMPLATE = 'order:<{order_id}>'

    def __init__(self, session: AsyncSession, redis_client: AsyncRedis):
        self._redis = redis_client
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

    async def _get_from_cache(self, order_id: UUID) -> DomainOrder | None:
        """ Забрать из кэша """

        key = self.CACHE_ORDER_KEY_TEMPLATE.format(order_id=order_id)
        from_cache = await self._redis.get(key)
        if from_cache is not None:
            await self._redis.expire(key, config.ORDER_CACHE_TTL)
            return DomainOrder.model_validate_json(from_cache)

    async def _cache_probed_earlier(self, order_id: UUID) -> bool:
        """ Запрашивался ли ранее. Если нет, регистрирует текущий запрос """

        last_request_key = self.CACHE_ORDER_LAST_REQUEST_KEY_TEMPLATE.format(order_id=order_id)

        # Помечаем последний запрос заказа
        if await self._redis.get(last_request_key) is None:
            await self._redis.set(
                last_request_key,
                str(datetime.now(tz=timezone.utc).replace(tzinfo=None)),
                ex=config.ORDER_CACHE_TTL
            )
            return False
        return True

    async def _put_to_cache(self, order: DomainOrder) -> None:
        """ Добавить в кэш """

        key = self.CACHE_ORDER_KEY_TEMPLATE.format(order_id=order.id)
        await self._redis.set(
            key,
            order.model_dump_json(),
            ex=config.ORDER_CACHE_TTL
        )

    async def _remove_from_cache(self, order_id: UUID) -> None:
        """ Удалить из кэша """

        key = self.CACHE_ORDER_KEY_TEMPLATE.format(order_id=order_id)
        await self._redis.delete(key)

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
        await self._remove_from_cache(id)
        return self._db_to_domain_model(from_db)

    async def get(self, order_id: UUID) -> DomainOrder | None:
        """ Заказ по ID """

        from_cache = await self._get_from_cache(order_id)
        if from_cache is not None:
            return from_cache

        query = select(DBOrder).where(DBOrder.id == order_id)
        async with self._session.begin():
            from_db = await self._session.scalar(query)
        if from_db is None:
            return

        order = self._db_to_domain_model(from_db)
        if await self._cache_probed_earlier(order_id):
            await self._put_to_cache(order)
        return order

    async def get_for_user(self, user_id: UUID) -> list[DomainOrder]:
        """ Заказы пользователя """

        query = select(DBOrder).where(DBOrder.user_id == user_id)
        async with self._session.begin():
            from_db = await self._session.scalars(query)
        return [self._db_to_domain_model(order) for order in from_db]
