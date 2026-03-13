from pydantic import BaseModel, EmailStr

class UserDto(BaseModel):
    login: str
    password: str
    name: str
    surname: str
    email: EmailStr