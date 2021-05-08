import uuid

from sqlalchemy import Boolean, Column, String
from sqlalchemy.dialects.postgresql import UUID

from ...database import Base


class Integration(Base):
    __tablename__ = "integration"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String)
    official = Column(Boolean, nullable=False, default=False)
    link = Column(String)
    public = Column(Boolean, nullable=False, default=False)
    owner_id = Column(String, index=True)
