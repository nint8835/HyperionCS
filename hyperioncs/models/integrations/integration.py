import uuid

from sqlalchemy import Boolean, Column, String
from sqlalchemy.dialects.postgresql import UUID

from ..base import Base, BaseDBModel


class Integration(Base, BaseDBModel):
    __tablename__ = "integration"

    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String)
    official = Column(Boolean, nullable=False, default=False)
    link = Column(String)
    public = Column(Boolean, nullable=False, default=False)
    owner_id = Column(String, index=True)
