from typing import List
from uuid import uuid4
from passlib.hash import pbkdf2_sha256
from pydantic import EmailStr
from sqlalchemy.orm import relationship, Mapped, declarative_base
from sqlalchemy import UUID, Column, String
from app.data.models.Role import Role
from app.data.models.UserRole import UserRole

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    login = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(255))
    roles: Mapped[List["Role"]] = relationship("Role",secondary=UserRole.__tablename__,back_populates="users",cascade="all, delete")

    def __init__(self,login: str,password: str,first_name: str,last_name: str,email: EmailStr):
        self.login = login
        self.password_hash = pbkdf2_sha256.hash(password)
        self.first_name = first_name
        self.last_name = last_name
        self.email = email

    def check_password(self, password: str):
        return pbkdf2_sha256.verify(password, self.password_hash)