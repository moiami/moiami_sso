import logging
from fastapi import APIRouter, Depends
from app.data.schemas.User import UserCreateDto
from app.services.SecurityService import get_tokens_data
from app.services.UserService import new_user as create_user

router = APIRouter(prefix='')

@router.post("/new_user")
async def new_user(new_user: UserCreateDto, current_user: str = Depends(get_tokens_data)):
    logging.info('POST: /new_user.')
    return await create_user(new_user,current_user)