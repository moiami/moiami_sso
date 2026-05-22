import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from src.data.models.token import Token
from src.data.schemas.user import UserCreateDto, UserLoginDto
from src.services.security_service import (
    get_refresh_tokens_data,
    validate_token,
)
from src.services.security_service import (
    login as security_login,
)
from src.services.security_service import (
    refresh as security_refresh,
)
from src.services.user_service import create_user

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post(
    "/login",
    summary="Вход пользователя в систему",
    description="Аутентификация пользователя по логину и паролю. "
    "Возвращает access_token и refresh_token для последующих запросов.",
    status_code=status.HTTP_200_OK,
)
async def auth(user_in: UserLoginDto, response: Response) -> dict[str, Any]:
    logging.info("POST: /login.")
    data = await security_login(user_in)
    response.headers["X-User-Id"] = str(data["id"])
    return data


@router.post(
    "/validate",
    summary="Валидация токена",
    description="Проверяет валидность JWT токена и возвращает информацию o пользователе.",
    status_code=status.HTTP_200_OK,
)
async def validate(
    response: Response, data: dict[str, Any] = Depends(validate_token)
) -> dict[str, Any]:
    logging.info("POST: /validate.")
    response.headers["X-User-Id"] = data["user_id"]
    response.headers["X-User-Role"] = data["user_roles"]
    return data


@router.post(
    "/refresh",
    summary="Обновление токенов",
    description="Получение новых access_token и refresh_token c использованием валидного refresh_token.",
    status_code=status.HTTP_200_OK,
)
async def refresh(data: tuple[Token, UUID] = Depends(get_refresh_tokens_data)) -> dict[str, str]:
    logging.info("POST: /refresh.")
    return await security_refresh(data[1], data[0])


@router.post(
    "/register",
    summary="Регистрация нового пользователя",
    description="Создание нового пользователя в системе. После успешной регистрации возвращает токены.",
    status_code=status.HTTP_200_OK,
)
async def register(new_user: UserCreateDto) -> dict[str, str]:
    logging.info("POST: /register.")
    return await create_user(new_user)
