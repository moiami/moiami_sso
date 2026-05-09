import logging
from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.data.schemas.role import (
    RoleCreateDto,
    RoleDeleteDto,
    RoleDto,
    RoleUpdateDto,
)
from src.services.role_service import (
    create_role,
    delete_role,
    update_role,
)
from src.services.role_service import (
    role as get_role,
)
from src.services.role_service import (
    roles as get_roles,
)
from src.services.security_service import get_access_tokens_data

router = APIRouter(prefix="/api/v1/roles", tags=["Roles"])


@router.get(
    "/roles",
    summary="Получить список всех ролей",
    description="Возвращает список ролей.",
    status_code=status.HTTP_200_OK,
)
async def roles_list(current_user: UUID = Depends(get_access_tokens_data)) -> list[RoleDto]:
    logging.info("GET: /roles.", current_user)
    return await get_roles()


@router.get(
    "/role",
    summary="Получить роль по ID",
    description="Возвращает данные роли по UUID.",
    status_code=status.HTTP_200_OK,
)
async def role_detail(id: UUID, _current_user: UUID = Depends(get_access_tokens_data)) -> RoleDto:
    logging.info("GET: /role.")
    return await get_role(id)


@router.post(
    "/create_role",
    summary="Создать новую роль",
    description="Создание новой роли. Доступно только пользователям c ролью `admin`.",
    status_code=status.HTTP_200_OK,
)
async def create_role_endpoint(
    new_role: RoleCreateDto, current_user: UUID = Depends(get_access_tokens_data)
) -> dict[str, str]:
    logging.info("POST: /create_role.")
    return await create_role(new_role, current_user)


@router.patch(
    "/update_role",
    summary="Обновить роль",
    description="Обновление данных роли. Доступно только пользователям c ролью `admin`.",
    status_code=status.HTTP_200_OK,
)
async def update_role_endpoint(
    updated_role: RoleUpdateDto, current_user: UUID = Depends(get_access_tokens_data)
) -> dict[str, str]:
    logging.info("PATCH: /update_role.")
    return await update_role(updated_role, current_user)


@router.delete(
    "/delete_role",
    summary="Удалить роль",
    description="Удаление роли. Доступно только пользователям c ролью `admin`.",
    status_code=status.HTTP_200_OK,
)
async def delete_role_endpoint(
    deleted_role: RoleDeleteDto, current_user: UUID = Depends(get_access_tokens_data)
) -> dict[str, str]:
    logging.info("DELETE: /delete_role.")
    return await delete_role(deleted_role, current_user)
