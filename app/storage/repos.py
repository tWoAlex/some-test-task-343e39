from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import User as DomainUser
from .models import User as DBUser


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
        from_db = await self._session.scalar(query)
        if from_db:
            return self._db_to_domain_model(from_db)
