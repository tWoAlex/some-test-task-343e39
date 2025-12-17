from uuid import UUID

from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


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
