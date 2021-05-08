import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import Column, Enum, ForeignKey, ForeignKeyConstraint, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ...base import Base, BaseDBModel
from .enums import TransactionState

if TYPE_CHECKING:
    from ...integrations import Integration
    from ..account import Account
    from ..currency import Currency


class Transaction(Base, BaseDBModel):
    __tablename__ = "transaction"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    amount = Column(Integer, nullable=False)
    state = Column(
        Enum(TransactionState), nullable=False, default=TransactionState.PENDING
    )
    description = Column(String)
    source_currency_id = Column(
        UUID(as_uuid=True), ForeignKey("currency.id"), index=True
    )
    source_account_id = Column(String, index=True)
    dest_currency_id = Column(UUID(as_uuid=True), ForeignKey("currency.id"), index=True)
    dest_account_id = Column(String, index=True)
    integration_id = Column(UUID(as_uuid=True), ForeignKey("integration.id"))

    source_currency = relationship("Currency", foreign_keys=[source_currency_id])
    source_account = relationship(
        "Account", foreign_keys=[source_currency_id, source_account_id]
    )
    dest_currency = relationship("Currency", foreign_keys=[dest_currency_id])
    dest_account = relationship(
        "Account", foreign_keys=[dest_currency_id, dest_account_id]
    )
    integration = relationship("Integration")

    __table_args__: Any = (
        ForeignKeyConstraint(
            ["source_currency_id", "source_account_id"],
            ["account.currency_id", "account.id"],
        ),
        ForeignKeyConstraint(
            ["dest_currency_id", "dest_account_id"],
            ["account.currency_id", "account.id"],
        ),
        {},
    )
