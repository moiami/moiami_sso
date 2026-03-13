from sqlalchemy import UUID, Column,ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class UserRole(Base):
    __tablename__ = "user_roles"
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )