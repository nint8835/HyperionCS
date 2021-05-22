import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..base import Base, BaseDBModel

if TYPE_CHECKING:
    from ..currencies import Currency
    from .integration import Integration


class IntegrationConnection(Base, BaseDBModel):
    __tablename__ = "integration_connection"

    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    integration_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("integration.id"), nullable=False, index=True
    )
    currency_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("currency.id"), nullable=False, index=True
    )
    last_used = Column(DateTime)

    integration: "Integration" = relationship("Integration")
    currency: "Currency" = relationship("Currency")
