import logging
from fastapi import APIRouter
from app.data.schemas.User import UserDto
from app.services.SecurityService import get_tokens_data,login as security_login, get_role as get_security_role
from app.services.UserService import new_user as create_user

router = APIRouter(prefix='')

@router.post("/new_user")
async def new_user(new_user: UserDto):
    logging.info('POST: /new_user.')
    return await create_user(new_user)