from uuid import UUID

from pydantic import BaseModel


class RoleDto(BaseModel):
    id: UUID
    name: str
    description: str


class RoleConnectDto(BaseModel):
    id: UUID


class RoleCreateDto(BaseModel):
    name: str
    description: str


class RoleUpdateDto(BaseModel):
    id: UUID
    name: str
    description: str


class RoleDeleteDto(BaseModel):
    id: UUID
