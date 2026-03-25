from uuid import uuid4

from passlib.hash import pbkdf2_sha256
from pydantic import EmailStr
from sqlalchemy import UUID, Column, String
from sqlalchemy.orm import Mapped, relationship

from src.data.models.base import Base
from src.data.models.role import Role
from src.data.models.user_role import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    login = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(255))
    roles: Mapped[list[Role]] = relationship(
        "Role", secondary=UserRole.__tablename__, back_populates="users", cascade="all, delete"
    )

    def __init__(
        self, login: str, password: str, first_name: str, last_name: str, email: EmailStr
    ) -> None:
        self.login = login
        self.password_hash = pbkdf2_sha256.hash(password)
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    def check_password(self, password: str) -> bool:
        return pbkdf2_sha256.verify(password, str(self.password_hash))

    def assign_role(self, role: Role) -> None:
        self.roles.append(role)
