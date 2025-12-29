from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hyperioncs.db import Base
from hyperioncs.db.models.utils import default_uuid_str

if TYPE_CHECKING:
    from .integration import Integration


class IntegrationToken(Base):
    __tablename__ = "integration_tokens"

    id: Mapped[str] = mapped_column(primary_key=True, default=default_uuid_str)
    integration_id: Mapped[str] = mapped_column(
        ForeignKey("integrations.id", ondelete="CASCADE")
    )

    integration: Mapped["Integration"] = relationship(lazy="raise")
