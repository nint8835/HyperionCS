from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..base import Base, GenericModel

if TYPE_CHECKING:
    from .currency import Currency


class Account(Base, GenericModel):
    __tablename__ = "account"

    currency_id = Column(
        UUID(as_uuid=True), ForeignKey("currency.id"), primary_key=True
    )
    id = Column(String, primary_key=True)
    balance = Column(Integer, nullable=False, default=0)

    currency = relationship("Currency")
