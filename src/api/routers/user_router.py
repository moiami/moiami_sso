import logging
from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.data.schemas.user import UserConnectRoleDto, UserDeleteDto, UserDto
from src.services.security_service import get_access_tokens_data
from src.services.user_service import (
    change_role as update_user_role,
)
from src.services.user_service import (
    delete_user,
)
from src.services.user_service import (
    user as get_user,
)
from src.services.user_service import (
    users as get_users,
)

router = APIRouter(prefix="/api/v1/user", tags=["Users"])


@router.get(
    "/users",
    summary="Получить список всех пользователей",
    description="Возвращает список всех пользователей c их ролями. Доступно только авторизованным пользователям.",
    status_code=status.HTTP_200_OK,
)
async def users_list(_current_user: UUID = Depends(get_access_tokens_data)) -> list[UserDto]:
    logging.info("GET: /users.")
    return await get_users()


@router.get(
    "/user",
    summary="Получить пользователя по ID",
    description="Возвращает данные конкретного пользователя по UUID.",
    status_code=status.HTTP_200_OK,
)
async def user_detail(id: UUID, _current_user: UUID = Depends(get_access_tokens_data)) -> UserDto:
    logging.info("GET: /user.")
    return await get_user(id)


@router.post(
    "/change_role",
    summary="Изменить роль пользователя",
    description="Назначает роль пользователю. Доступно только пользователям c ролью `admin`.",
    status_code=status.HTTP_200_OK,
)
async def change_role(
    data: UserConnectRoleDto, current_user: UUID = Depends(get_access_tokens_data)
) -> dict[str, str]:
    logging.info("POST: /change_role.")
    return await update_user_role(data, current_user)


@router.delete(
    "/delete_user",
    summary="Удалить пользователя",
    description="Удаляет пользователя из системы. Доступно только пользователям c ролью `admin`.",
    status_code=status.HTTP_200_OK,
)
async def delete(
    deleted_user: UserDeleteDto, current_user: UUID = Depends(get_access_tokens_data)
) -> dict[str, str]:
    logging.info("DELETE: /delete_user.")
    return await delete_user(deleted_user, current_user)
