import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends

from src.data.models.token import Token
from src.data.schemas.user import UserCreateDto, UserLoginDto
from src.services.security_service import get_refresh_tokens_data, validate_token
from src.services.security_service import login as security_login
from src.services.security_service import refresh as security_refresh
from src.services.user_service import create_user

router = APIRouter(prefix="/api/v1/auth")


@router.post("/login")
async def auth(user_in: UserLoginDto) -> dict[str, str]:
    logging.info("POST: /login.")
    return await security_login(user_in)


@router.post("/validate")
async def validate(data: dict[str, str] = Depends(validate_token)) -> dict[str, Any]:
    logging.info("POST: /validate.")
    return data


@router.post("/refresh")
async def refresh(data: tuple[Token, UUID] = Depends(get_refresh_tokens_data)) -> dict[str, str]:
    logging.info("POST: /refresh.")
    return await security_refresh(data[1], data[0])


@router.post("/register")
async def create(new_user: UserCreateDto) -> dict[str, str]:
    logging.info("POST: /create_user.")
    return await create_user(new_user)
