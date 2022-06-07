import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

import hyperioncs.models.currencies as currencies
import hyperioncs.models.integrations as integrations
from hyperioncs.models.base import Base, BaseDBModel
from hyperioncs.models.utils import default_uuid_str


class IntegrationConnection(Base, BaseDBModel):
    __tablename__ = "integration_connection"

    id: str = Column(String, primary_key=True, default=default_uuid_str)
    integration_id: str = Column(
        String, ForeignKey("integration.id"), nullable=False, index=True
    )
    currency_id: str = Column(
        String, ForeignKey("currency.id"), nullable=False, index=True
    )
    last_used: Optional[datetime] = Column(DateTime)

    integration: "integrations.Integration" = relationship("Integration")
    currency: "currencies.Currency" = relationship("Currency")
