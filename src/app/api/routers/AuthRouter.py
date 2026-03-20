import logging
from fastapi import Depends, APIRouter
from app.data.schemas.User import UserLoginDto
from app.services.SecurityService import get_tokens_data,login as security_login, refresh as security_refresh

router = APIRouter(prefix='')

@router.post("/login")
async def login(user_in: UserLoginDto):
    logging.info('POST: /login.')
    return await security_login(user_in)

@router.get("/refresh")
async def refresh(current_user: str = Depends(get_tokens_data)):
    logging.info('GET: /refresh.')
    return await security_refresh(current_user)