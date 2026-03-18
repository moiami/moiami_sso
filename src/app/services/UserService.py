from app.data.models.Role import Role
from app.data.models.User import User
from app.data.repositories.Repository import insert_user, get_user
from app.data.schemas.User import UserCreateDto

async def new_user(user_in: UserCreateDto,current_user: str):
    auth_user = await get_user(current_user)
    if list(auth_user.roles)[0].name == "admin":
        user = User(user_in.login, user_in.password,user_in.name,user_in.surname,user_in.email)
        role = Role(user_in.role.name,user_in.role.description)
        user.roles.append(role)
        await insert_user(user)
        return {"Info": user_in.dict()}
    else:
        return {"error": "you not have permission"}