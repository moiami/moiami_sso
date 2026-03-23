import logging
from uuid import UUID

from fastapi import APIRouter, Depends

from app.data.models.user import User
from app.data.schemas.user import UserCreateDto, UserDeleteDto, UserDto, UserUpdateDto
from app.services.security_service import get_access_tokens_data
from app.services.user_service import create_user, delete_user, get_users, update_user
from app.services.user_service import user as get_user

router = APIRouter(prefix='')


@router.get("/users")
async def users(current_user: UUID = Depends(get_access_tokens_data)) -> list[User]:
    logging.info('GET: /users.',current_user)
    return await get_users()


@router.get("/user")
async def user(id: UUID, current_user: UUID = Depends(get_access_tokens_data)) -> UserDto:
    logging.info('GET: /user.',current_user)
    return await get_user(id)


@router.post("/create_user")
async def create(new_user: UserCreateDto, current_user: UUID = Depends(get_access_tokens_data)) -> dict[str, str]:
    logging.info('POST: /create_user.',current_user)
    return await create_user(new_user, current_user)


@router.patch("/update_user")
async def update(updated_user: UserUpdateDto, current_user: UUID = Depends(get_access_tokens_data)) -> dict[str, str]:
    logging.info('PATCH: /update_user.',current_user)
    return await update_user(updated_user, current_user)


@router.delete("/delete_user")
async def delete(deleted_user: UserDeleteDto, current_user: UUID = Depends(get_access_tokens_data)) -> dict[str, str]:
    logging.info('DELETE: /delete_user.',current_user)
    return await delete_user(deleted_user, current_user)
