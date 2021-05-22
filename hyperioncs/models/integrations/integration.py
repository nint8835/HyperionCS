import uuid
from typing import Optional

from sqlalchemy import Boolean, Column, String
from sqlalchemy.dialects.postgresql import UUID

from ..base import Base, BaseDBModel


class Integration(Base, BaseDBModel):
    __tablename__ = "integration"

    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: str = Column(String, nullable=False)
    description: Optional[str] = Column(String)
    official: bool = Column(Boolean, nullable=False, default=False)
    link: Optional[str] = Column(String)
    public: bool = Column(Boolean, nullable=False, default=False)
    owner_id: str = Column(String, index=True)
