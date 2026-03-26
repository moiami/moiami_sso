import datetime
from typing import Any
from uuid import UUID, uuid4

import jwt
from fastapi import Depends, HTTPException
from starlette import status

from src.constants import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_MINUTES,
    SCHEME,
    SECRET_KEY,
)
from src.data.models.token import Token
from src.data.models.user import User
from src.data.repositories.auth_repository import get_token, insert_token, update_token
from src.data.repositories.user_repository import get_user_by_id, get_user_by_login
from src.data.schemas.user import UserLoginDto


async def login(user_in: UserLoginDto) -> dict[str, str]:
    try:
        user: User = await get_user_by_login(user_in.login)
        if user_in.login == user.login and user.check_password(user_in.password):
            id_refresh: UUID = uuid4()
            access_token = await create_jwt(
                {"id": str(user.id), "roles": [role.name for role in list(user.roles)]}, "access"
            )
            refresh_token = await create_jwt(
                {"id": str(id_refresh), "user_id": str(user.id)}, "refresh"
            )
            await insert_token(Token(id_refresh, refresh_token, True))
            return {
                "id": str(user.id),
                "access_token": access_token,
                "token_type": "bearer",
                "refresh_token": refresh_token,
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="incorrect data"
        ) from e
    return {"Info": "Login Failed"}


async def refresh(current_user: UUID, token: Token) -> dict[str, str]:
    try:
        user: User = await get_user_by_id(current_user)
        id_refresh: UUID = uuid4()
        access_token: str = await create_jwt(
            {"id": str(user.id), "roles": [role.name for role in list(user.roles)]}, "access"
        )
        refresh_token: str = await create_jwt(
            {"id": str(id_refresh), "user_id": str(user.id)}, "refresh"
        )
        token.status = False
        await update_token(token)
        await insert_token(Token(id_refresh, refresh_token, True))
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": refresh_token,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR"
        ) from e


async def create_jwt(data: dict, type: str) -> str:
    try:
        encode_data = data.copy()
        time = datetime.datetime.now(datetime.UTC)
        if type == "access":
            time += datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        else:
            time += datetime.timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
        encode_data.update({"exp": time})
        return jwt.encode(encode_data, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR"
        ) from e


async def validate_token(token: str = Depends(SCHEME)) -> dict[str, str]:
    try:
        jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        return {"info": "valid"}
    except jwt.ExpiredSignatureError:
        return {"info": "The token has expired"}
    except jwt.InvalidTokenError:
        return {"info": "Invalid token"}


async def get_refresh_tokens_data(token: str = Depends(SCHEME)) -> tuple[Token, UUID]:
    try:
        data: dict[str, Any] = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        token_from_db: Token = await get_token(UUID(data.get("id")))
        if token_from_db is None or token_from_db.status is False:
            raise jwt.InvalidTokenError
        return token_from_db, UUID(data.get("user_id"))
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(status_code=401, detail="The token has expired") from e
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail="Invalid token") from e


async def get_access_tokens_data(token: str = Depends(SCHEME)) -> UUID:
    try:
        data: dict[str, Any] = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        return UUID(data.get("id"))
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="The token has expired"
        ) from e
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from e
