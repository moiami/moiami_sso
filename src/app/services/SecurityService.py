import jwt
import datetime
from fastapi import Depends, HTTPException
from typing import Dict
from starlette import status

from app.data.repositories.UserRepository import get_user, get_users
from app.data.schemas.User import UserLoginDto
from constants import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SCHEME, REFRESH_TOKEN_EXPIRE_MINUTES

async def login(user_in: UserLoginDto):
    users = await get_users()
    for user in users:
        if user_in.login == user.login or user.check_password(user_in.password):
            access_token = await create_jwt({"sub": str(user.id)},"access")
            refresh_token = await create_jwt({"sub": str(user.id)},"refresh")
            return {"access_token": access_token, "token_type": "bearer","refresh_token": refresh_token}
    return {"error": "Invalid credentials"}

async def refresh(current_user):
    user = await get_user(current_user)
    access_token = await create_jwt({"sub": user.login},"access")
    return {"access_token": access_token, "token_type": "bearer"}

async def create_jwt(data: Dict,type:str):
    encode_data = data.copy()
    time = datetime.datetime.utcnow()
    if type == "access":
        time+=datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        time+=datetime.timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    encode_data.update({"exp":time })
    return jwt.encode(encode_data, SECRET_KEY, algorithm=ALGORITHM)

async def get_tokens_data(token: str = Depends(SCHEME)):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        return data.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="The token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")