from uuid import uuid4

from sqlalchemy import UUID, Column, String, Text
from sqlalchemy.orm import relationship

from src.data.models.base import Base
from src.data.models.user_role import UserRole


class Role(Base):
    __tablename__ = "roles"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    name = Column(String(20), index=True, nullable=False)
    description = Column(Text, nullable=False)
    users = relationship(
        "User", secondary=UserRole.__tablename__, back_populates="roles", cascade="all, delete"
    )

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description
