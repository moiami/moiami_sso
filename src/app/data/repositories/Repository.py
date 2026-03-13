def get_users():
    DATA = [
        {"login": "1111", "password": "1234"}
    ]
    return DATA

def get_user(username: str):
    """
    Должна быть проверка на наличие пользователя в бд, но пока заглушка
    """
    for user in get_users():
        print(user.get("login"))
        if user.get("login") == username:
            return user
    return None