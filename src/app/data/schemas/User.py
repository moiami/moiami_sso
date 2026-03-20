from uuid import UUID

from pydantic import BaseModel, EmailStr
from app.data.schemas.Role import RoleDto

class UserCreateDto(BaseModel):
    login: str
    password: str
    name: str
    surname: str
    email: EmailStr
    roles: list[RoleDto]

class UserUpdateDto(BaseModel):
    id: UUID
    password: str
    name: str
    surname: str
    email: EmailStr
    roles: list[RoleDto]

class UserDeleteDto(BaseModel):
    id: UUID

class UserLoginDto(BaseModel):
    login: str
    password: str

class UserDto(BaseModel):
    id: UUID
    login: str
    name: str
    surname: str
    email: EmailStr
    roles: list[RoleDto]