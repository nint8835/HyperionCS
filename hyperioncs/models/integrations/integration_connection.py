import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ...database import Base

if TYPE_CHECKING:
    from ..currencies import Currency
    from .integration import Integration


class IntegrationConnection(Base):
    __tablename__ = "integration_connection"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    integration_id = Column(
        UUID(as_uuid=True), ForeignKey("integration.id"), nullable=False, index=True
    )
    currency_id = Column(
        UUID(as_uuid=True), ForeignKey("currency.id"), nullable=False, index=True
    )
    last_used = Column(DateTime)

    integration = relationship("Integration")
    currency = relationship("Currency")
