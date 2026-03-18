import logging
from fastapi import Depends, APIRouter,Request
from app.data.schemas.User import UserLoginDto
from app.services.SecurityService import get_tokens_data,login as security_login, get_role as get_security_role, refresh as security_refresh

router = APIRouter(prefix='')

@router.post("/login")
async def login(user_in: UserLoginDto):
    logging.info('POST: /login.')
    return await security_login(user_in)

@router.get("/refresh")
async def refresh(current_user: str = Depends(get_tokens_data)):
    logging.info('GET: /refresh.')
    return await security_refresh(current_user)

@router.get("/role")
async def get_role(current_user: str = Depends(get_tokens_data)):
    logging.info('GET: /role.')
    return await get_security_role(current_user)