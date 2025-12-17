from string import ascii_letters, digits, punctuation

from fastapi import APIRouter, Depends, HTTPException, Response, status
from dependency_injector.wiring import Provide, inject
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.auth import auth, config as auth_config
from app.containers import Container
from app.services import UserService


router = APIRouter()


PASSWORD_ALLOWED_CHARACTERS = ascii_letters + digits + punctuation


class UserRegistrationSchema(BaseModel):
    """ Данные для регистрации """

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator('password', mode='after')
    def validate_password(cls, value: str):
        """ Проверка непечатных символов в пароле """

        if any(map(lambda x: x not in PASSWORD_ALLOWED_CHARACTERS, value)):
            raise ValueError(f"Only <{PASSWORD_ALLOWED_CHARACTERS}> characters allowed")
        return value


class UserLoginSchema(UserRegistrationSchema):
    """ Данные для логина """


@router.post(
    path='/register',
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация"
)
@inject
async def register(
    credentials: UserRegistrationSchema,
    user_service: UserService = Depends(Provide[Container.user_service])
):
    try:
        await user_service.register(
            email=credentials.email,
            password=credentials.password
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={'message': str(exc)}
        )


@router.post(
    path='/login',
    status_code=status.HTTP_200_OK,
    summary="Аутентификация"
)
@inject
async def login(
    credentials: UserLoginSchema,
    response: Response,
    user_service: UserService = Depends(Provide[Container.user_service])
):
    try:
        user = await user_service.login(
            email=credentials.email,
            password=credentials.password
        )
    except KeyError, ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={'message': "User not found or wrong password"}
        )

    token = auth.create_access_token(uid=user.id.hex)
    response.set_cookie(auth_config.JWT_ACCESS_COOKIE_NAME, token)
    return {'access_token': token}
