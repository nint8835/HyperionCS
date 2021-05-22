import uuid
from typing import TYPE_CHECKING, Any, List, Optional, Union

from sqlalchemy import (
    Column,
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    or_,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session, relationship

from ...base import Base, BaseDBModel
from ..account import Account
from .enums import TransactionState

if TYPE_CHECKING:
    from ...integrations import Integration
    from ..currency import Currency


class Transaction(Base, BaseDBModel):
    __tablename__ = "transaction"

    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    amount: int = Column(Integer, nullable=False)
    state: TransactionState = Column(
        Enum(TransactionState), nullable=False, default=TransactionState.PENDING
    )
    state_reason: Optional[str] = Column(String)
    description: Optional[str] = Column(String)
    source_currency_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("currency.id"), index=True
    )
    source_account_id: str = Column(String, index=True)
    dest_currency_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("currency.id"), index=True
    )
    dest_account_id: str = Column(String, index=True)
    integration_id: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey("integration.id"))

    source_currency: "Currency" = relationship(
        "Currency", foreign_keys=[source_currency_id], overlaps="source_account"
    )
    source_account: "Account" = relationship(
        "Account",
        foreign_keys=[source_currency_id, source_account_id],
        overlaps="source_currency",
    )
    dest_currency: "Currency" = relationship(
        "Currency", foreign_keys=[dest_currency_id], overlaps="dest_account"
    )
    dest_account: "Account" = relationship(
        "Account",
        foreign_keys=[dest_currency_id, dest_account_id],
        overlaps="dest_currency",
    )
    integration: "Integration" = relationship("Integration")

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

    def execute(self, db: Session) -> None:
        # TODO: Maybe add a check to ensure the transaction is pending here?

        src_account: Optional["Account"] = (
            db.query(Account)
            .with_for_update()
            .filter_by(id=self.source_account_id, currency_id=self.source_currency_id)
            .first()
        )

        dest_account = (
            db.query(Account)
            .with_for_update()
            .filter_by(id=self.dest_account_id, currency_id=self.dest_currency_id)
            .first()
        )

        if src_account is None:
            self.state = TransactionState.FAILED
            self.state_reason = "Source account could not be found."
            self.set_modified()
            db.commit()
            return

        if dest_account is None:
            self.state = TransactionState.FAILED
            self.state_reason = "Destination account could not be found."
            self.set_modified()
            db.commit()
            return

        if src_account.balance < self.amount and not src_account.system_account:
            self.state = TransactionState.FAILED
            self.state_reason = "Source account does not have sufficient balance to cover this transaction."
            self.set_modified()
            db.commit()
            return

        src_account.balance -= self.amount
        dest_account.balance += self.amount

        self.state = TransactionState.COMPLETE
        self.set_modified()

        db.commit()

    @classmethod
    def get_transaction(
        cls,
        db: Session,
        currency_id: Union[uuid.UUID, str],
        transaction_id: Union[uuid.UUID, str],
    ) -> Optional["Transaction"]:
        return (
            db.query(Transaction)
            .filter(
                or_(
                    Transaction.source_currency_id == currency_id,
                    Transaction.dest_currency_id == currency_id,
                )
            )
            .filter_by(id=transaction_id)
            .first()
        )

    @classmethod
    def get_transactions_for_currency(
        cls, db: Session, currency_id: Union[uuid.UUID, str]
    ) -> List["Transaction"]:
        return (
            db.query(Transaction)
            .filter(
                or_(
                    Transaction.source_currency_id == currency_id,
                    Transaction.dest_currency_id == currency_id,
                )
            )
            .all()
        )
