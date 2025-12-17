from app.storage.repos import UserRepository

from app.domain.models import User as DomainUser
from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()


class UserService:
    """ Сервис для управления пользователями """

    def __init__(self, repo: UserRepository):
        self._repo = repo

    async def register(self, email: str, password: str) -> None:
        """ Зарегистрировать пользователя """

        new_user = DomainUser(
            email=email,
            hashed_password=password_hash.hash(password)
        )
        try:
            await self._repo.add(new_user)
        except ValueError:
            raise

    async def login(self, email: str, password: str) -> DomainUser:
        """
        Проверить пару логин/пароль пользователя

        :return: True = пароль совпал, False = пароль не совпал
        :raises KeyError: Пользователь не найден
        :raises ValueError: Пароль не совпал
        """

        user = await self._repo.get_by_email(email)
        if user is None:
            raise KeyError("User not found")
        if not password_hash.verify(password, user.hashed_password):
            raise ValueError("Wrong password")
        return user
