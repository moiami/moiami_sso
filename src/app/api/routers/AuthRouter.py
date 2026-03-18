import logging
from fastapi import Depends, APIRouter,Request
from app.data.schemas.User import UserLoginDto
from app.services.SecurityService import get_tokens_data,login as security_login, get_role as get_security_role

router = APIRouter(prefix='')

@router.post("/login")
async def login(user_in: UserLoginDto):
    logging.info('POST: /login.')
    return await security_login(user_in)

@router.get("/refresh")
async def refresh(request: Request):
    #переделать
    request.cookies.get("refresh_token")
    return {"info": "Success"}

@router.get("/role")
async def get_role(current_user: str = Depends(get_tokens_data)):
    logging.info('GET: /role.')
    return await get_security_role(current_user)