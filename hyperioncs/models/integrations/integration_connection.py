import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

import hyperioncs.models.currencies as currencies
import hyperioncs.models.integrations as integrations
from hyperioncs.models.base import Base, BaseDBModel


class IntegrationConnection(Base, BaseDBModel):
    __tablename__ = "integration_connection"

    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    integration_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("integration.id"), nullable=False, index=True
    )
    currency_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("currency.id"), nullable=False, index=True
    )
    last_used: Optional[datetime] = Column(DateTime)

    integration: "integrations.Integration" = relationship("Integration")
    currency: "currencies.Currency" = relationship("Currency")
