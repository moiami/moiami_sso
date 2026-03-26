"""
async def roles() -> list[Role] | dict[str, str]:
    try:
        roles_arr: list[Role] = await get_roles()
        if roles_arr is None:
            raise Exception
        return roles_arr
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR"
        ) from e


async def role(id: UUID) -> RoleDto:
    try:
        role: Role = await get_role(id)
        if role is None:
            raise TypeError
        role_dto: RoleDto = RoleDto(
            id=UUID(str(role.id)), name=str(role.name), description=str(role.description)
        )
        return role_dto
    except TypeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND") from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR"
        ) from e


async def create_role(role_in: RoleCreateDto, current_user: UUID) -> dict[str, str]:
    try:
        auth_user: User = await get_user_by_id(current_user)
        if auth_user is None:
            raise Exception
        roles: list[Role] = list(auth_user.roles)
        if any(role.name == ADMIN_USERNAME for role in roles):
            role: Role = Role(role_in.name, role_in.description)
            await insert(role)
            return {"Info": "Success"}
        raise ValueError
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN") from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR"
        ) from e


async def update_role(role_in: RoleUpdateDto, current_user: UUID) -> dict[str, str]:
    try:
        auth_user: User = await get_user_by_id(current_user)
        if auth_user is None:
            raise Exception
        if any(role.name == ADMIN_USERNAME for role in list(auth_user.roles)):
            await update(role_in)
            return {"Info": "Success"}
        raise ValueError
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN") from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR"
        ) from e


async def delete_role(role_in: RoleDeleteDto, current_user: UUID) -> dict[str, str]:
    try:
        auth_user: User = await get_user_by_id(current_user)
        if auth_user is None:
            raise Exception
        if any(role.name == ADMIN_USERNAME for role in list(auth_user.roles)):
            await delete(role_in.id)
            return {"Info": "Success"}
        raise ValueError
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN") from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="INTERNAL SERVER ERROR"
        ) from e
"""
