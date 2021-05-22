import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from ..base import Base, BaseDBModel


class Currency(Base, BaseDBModel):
    __tablename__ = "currency"

    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, index=True, nullable=False)
    singular_form = Column(String, nullable=False)
    plural_form = Column(String, nullable=False)
    shortcode = Column(String, unique=True, index=True, nullable=False)
    owner_id = Column(String, index=True, nullable=False)
