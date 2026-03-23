from uuid import uuid4

from sqlalchemy import UUID, Boolean, Column, Text

from app.data.models.base import Base


class Token(Base):
    __tablename__ = "tokens"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    token = Column(Text, index=True, nullable=False)
    status = Column(Boolean, nullable=False)

    def __init__(self,id:UUID, token: str, status: bool) -> None:
        self.id = id
        self.token = token
        self.status = status
