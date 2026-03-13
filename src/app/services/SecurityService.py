import jwt
import datetime
from fastapi import Depends
from typing import Dict
from app.data.repositories.Repository import get_user, get_users
from app.data.schemas.User import UserDto
from constants import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SCHEME

def login(user_in: UserDto):
    for user in get_users():
        if user_in.login == user.get("login") and user_in.password == user.get("password"):
            token = create_jwt({"sub": user.get("login")})
            return {"access_token": token, "token_type": "bearer"}
    return {"error": "Invalid credentials"}

def get_role(current_user: str):
    user = get_user(current_user)
    if user:
        return user
    return {"error": "User not found"}

def create_jwt(data: Dict):
    encode_data = data.copy()
    encode_data.update({"exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)})
    return jwt.encode(encode_data, SECRET_KEY, algorithm=ALGORITHM)

def get_tokens_data(token: str = Depends(SCHEME)):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        print(data)
        return data.get("sub")
    except jwt.ExpiredSignatureError:
        pass  # Обработка ошибки истечения срока действия токена
    except jwt.InvalidTokenError:
        pass  # Обработка ошибки недействительного токена
