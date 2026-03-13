import logging
from fastapi import Depends, APIRouter,Request

from app.data.schemas.User import UserDto
from app.services.SecurityService import get_tokens_data,login as security_login, get_role as get_security_role

router = APIRouter(prefix='')

@router.post("/login")
async def login(user_in: UserDto):
    logging.info('POST: /login. Data:' + user_in.login + ' ' + user_in.password)
    return security_login(user_in)

@router.get("/refresh")
async def refresh(request: Request):
    request.cookies.get("refresh_token")
    return {"info": "Success"}

@router.get("/role")
async def get_role(current_user: str = Depends(get_tokens_data)):
    logging.info('GET: /role. Data:' + current_user)
    return get_security_role(current_user)