from uuid import UUID

from pydantic import BaseModel


class RoleDto(BaseModel):
    id: UUID
    name: str
    description: str


class RoleCreateDto(BaseModel):
    name: str
    description: str


class RoleUpdateDto(BaseModel):
    id: UUID
    name: str
    description: str


class RoleDeleteDto(BaseModel):
    id: UUID
