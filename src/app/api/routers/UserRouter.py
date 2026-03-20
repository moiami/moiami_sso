import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from app.data.schemas.User import UserCreateDto, UserUpdateDto, UserDeleteDto
from app.services.SecurityService import get_tokens_data
from app.services.UserService import create_user, update_user, delete_user, get_users, user as get_user

router = APIRouter(prefix='')


@router.get("/users")
async def users(current_user: str = Depends(get_tokens_data)):
    logging.info('GET: /users.')
    return await get_users()


@router.get("/user")
async def user(id: UUID, current_user: str = Depends(get_tokens_data)):
    logging.info('GET: /user.')
    return await get_user(id)


@router.post("/create_user")
async def create(new_user: UserCreateDto, current_user: str = Depends(get_tokens_data)):
    logging.info('POST: /create_user.')
    return await create_user(new_user, current_user)


@router.patch("/update_user")
async def update(updated_user: UserUpdateDto, current_user: str = Depends(get_tokens_data)):
    logging.info('PATCH: /update_user.')
    return await update_user(updated_user, current_user)


@router.delete("/delete_user")
async def delete(deleted_user: UserDeleteDto, current_user: str = Depends(get_tokens_data)):
    logging.info('DELETE: /delete_user.')
    return await delete_user(deleted_user, current_user)
