from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

import hyperioncs.models.currencies as currencies
import hyperioncs.models.integrations as integrations
from hyperioncs.models.base import Base, BaseDBModel
from hyperioncs.models.utils import default_uuid_str


class IntegrationConnection(Base, BaseDBModel):
    __tablename__ = "integration_connection"

    id: Mapped[str] = mapped_column(primary_key=True, default=default_uuid_str)
    integration_id: Mapped[str] = mapped_column(
        ForeignKey("integration.id"), index=True
    )
    currency_id: Mapped[str] = mapped_column(ForeignKey("currency.id"), index=True)
    last_used: Mapped[Optional[datetime]]

    integration: Mapped["integrations.Integration"] = relationship()
    currency: Mapped["currencies.Currency"] = relationship()
