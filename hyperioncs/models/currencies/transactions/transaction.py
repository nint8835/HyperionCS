from typing import Any, List, Optional

from sqlalchemy import (
    ForeignKey,
    ForeignKeyConstraint,
    or_,
)
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

import hyperioncs.models.currencies as currencies
import hyperioncs.models.integrations as integrations
from hyperioncs.models.base import Base, BaseDBModel
from hyperioncs.models.utils import default_uuid_str

from .enums import TransactionState


class Transaction(Base, BaseDBModel):
    __tablename__ = "transaction"

    id: Mapped[str] = mapped_column(primary_key=True, default=default_uuid_str)
    amount: Mapped[int]
    state: Mapped[TransactionState] = mapped_column(default=TransactionState.PENDING)
    state_reason: Mapped[Optional[str]]
    description: Mapped[Optional[str]]
    source_currency_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("currency.id"), index=True
    )
    source_account_id: Mapped[Optional[str]] = mapped_column(index=True)
    dest_currency_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("currency.id"), index=True
    )
    dest_account_id: Mapped[Optional[str]] = mapped_column(index=True)
    integration_id: Mapped[Optional[str]] = mapped_column(ForeignKey("integration.id"))

    source_currency: Mapped["currencies.Currency"] = relationship(
        foreign_keys=[source_currency_id], overlaps="source_account"
    )
    source_account: Mapped["currencies.Account"] = relationship(
        "Account",
        foreign_keys=[source_currency_id, source_account_id],
        overlaps="source_currency",
    )
    dest_currency: Mapped["currencies.Currency"] = relationship(
        foreign_keys=[dest_currency_id], overlaps="dest_account"
    )
    dest_account: Mapped["currencies.Account"] = relationship(
        "Account",
        foreign_keys=[dest_currency_id, dest_account_id],
        overlaps="dest_currency",
    )
    integration: Mapped["integrations.Integration"] = relationship()

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

        src_account: Optional["currencies.Account"] = (
            db.query(currencies.Account)
            .with_for_update()
            .filter_by(id=self.source_account_id, currency_id=self.source_currency_id)
            .first()
        )

        dest_account = (
            db.query(currencies.Account)
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

    def cancel(self, db: Session, reason: Optional[str] = None) -> None:
        self.state = TransactionState.CANCELLED

        if reason is not None:
            self.state_reason = reason

        self.set_modified()
        db.commit()

    @classmethod
    def get_transaction(
        cls,
        db: Session,
        currency_id: str,
        transaction_id: str,
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
        cls, db: Session, currency_id: str
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
