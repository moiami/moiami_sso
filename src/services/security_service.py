import datetime
from typing import Any
from uuid import UUID, uuid4

import jwt
from fastapi import Depends, HTTPException
from starlette import status

from src.constants import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    CLIENT_ID,
    ISSUER_URL,
    PRIVATE_KEY,
    PUBLIC_KEY,
    REFRESH_TOKEN_EXPIRE_MINUTES,
    SCHEME,
)
from src.data.models.token import Token
from src.data.models.user import User
from src.data.repositories.auth_repository import get_token, insert_token, update_token
from src.data.repositories.user_repository import get_user_by_id, get_user_by_login
from src.data.schemas.user import UserLoginDto


async def login(user_in: UserLoginDto) -> dict[str, Any]:
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
                "login": str(user.login),
                "name": str(user.first_name),
                "surname": str(user.last_name),
                "email": str(user.email),
                "roles": [str(role.name) for role in user.roles],
                "access_token": access_token,
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
            "refresh_token": refresh_token,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR"
        ) from e


async def create_jwt(data: dict, type: str) -> str:
    encode_data = data.copy()
    time = datetime.datetime.now(datetime.UTC)
    expire = ACCESS_TOKEN_EXPIRE_MINUTES if type == "access" else REFRESH_TOKEN_EXPIRE_MINUTES
    encode_data.update(
        {
            "sub": data.get("id"),
            "exp": time + datetime.timedelta(minutes=expire),
            "iat": time,
            "iss": ISSUER_URL,
            "aud": CLIENT_ID,
        }
    )
    return jwt.encode(encode_data, PRIVATE_KEY, algorithm=ALGORITHM)


async def validate_token(token: str = Depends(SCHEME)) -> dict[str, Any]:
    try:
        data: dict[str, Any] = jwt.decode(
            token, PUBLIC_KEY, algorithms=[ALGORITHM], audience=CLIENT_ID, issuer=ISSUER_URL
        )
        user: User = await get_user_by_id(UUID(str(data.get("id"))))

        return {
            "user_id": str(data.get("id")),
            "user_roles": str([role.name for role in user.roles]),
            "is_valid": "True",
        }

    except jwt.ExpiredSignatureError as e:
        raise HTTPException(
            status_code=401,
            detail={
                "is_valid": "False",
            },
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail={
                "is_valid": "False",
            },
        ) from e


async def get_refresh_tokens_data(token: str = Depends(SCHEME)) -> tuple[Token, UUID]:
    try:
        data = jwt.decode(
            token, PUBLIC_KEY, algorithms=[ALGORITHM], audience=CLIENT_ID, issuer=ISSUER_URL
        )
        token_from_db: Token = await get_token(UUID(data.get("id")))
        if token_from_db is None or token_from_db.status is False:
            raise jwt.InvalidTokenError
        return token_from_db, UUID(data.get("user_id"))
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(status_code=401, detail="The token has expired") from e
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token") from e


async def get_access_tokens_data(token: str = Depends(SCHEME)) -> UUID:
    try:
        data = jwt.decode(
            token, PUBLIC_KEY, algorithms=[ALGORITHM], audience=CLIENT_ID, issuer=ISSUER_URL
        )
        return UUID(data.get("id"))
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="The token has expired"
        ) from e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from e
