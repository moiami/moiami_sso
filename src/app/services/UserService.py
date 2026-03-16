from app.data.models.Role import Role
from app.data.models.User import User
from app.data.repositories.Repository import insert_user, insert_role
from app.data.schemas.User import UserDto

async def new_user(user_in: UserDto):
    new_user = User(user_in.login, user_in.password,user_in.name,user_in.surname,user_in.email)
    role = Role("admin","kefmlkwefmwekf")
    new_user.roles.append(role)
    await insert_user(new_user)
    return {"Infor": user_in.dict()}