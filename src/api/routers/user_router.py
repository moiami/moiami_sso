import logging
from uuid import UUID

from fastapi import APIRouter, Depends

from src.data.schemas.user import UserConnectRoleDto, UserDeleteDto, UserDto
from src.services.security_service import get_access_tokens_data
from src.services.user_service import change_role as update_user_role
from src.services.user_service import delete_user
from src.services.user_service import user as get_user
from src.services.user_service import users as get_users

router = APIRouter(prefix="")


@router.get("/users")
async def users(_current_user: UUID = Depends(get_access_tokens_data)) -> list[UserDto]:
    logging.info("GET: /users.")
    return await get_users()


@router.get("/user")
async def user(id: UUID, _current_user: UUID = Depends(get_access_tokens_data)) -> UserDto:
    logging.info("GET: /user.")
    return await get_user(id)


@router.post("/change_role")
async def change_role(
    data: UserConnectRoleDto, current_user: UUID = Depends(get_access_tokens_data)
) -> dict[str, str]:
    logging.info("POST: /create_user.")
    return await update_user_role(data, current_user)


"""
@router.patch("/update_user")
async def update(updated_user: UserUpdateDto, current_user: UUID = Depends(get_access_tokens_data)) -> dict[str, str]:
    logging.info('PATCH: /update_user.')
    return await update_user(updated_user, current_user)
"""


@router.delete("/delete_user")
async def delete(
    deleted_user: UserDeleteDto, current_user: UUID = Depends(get_access_tokens_data)
) -> dict[str, str]:
    logging.info("DELETE: /delete_user.")
    return await delete_user(deleted_user, current_user)
