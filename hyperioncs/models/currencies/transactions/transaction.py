from typing import Any, Optional, Sequence

from sqlalchemy import (
    ForeignKey,
    ForeignKeyConstraint,
    select,
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
    currency_id: Mapped[str] = mapped_column(ForeignKey("currency.id"), index=True)
    source_account_id: Mapped[Optional[str]] = mapped_column(index=True)
    dest_account_id: Mapped[Optional[str]] = mapped_column(index=True)
    integration_id: Mapped[Optional[str]] = mapped_column(ForeignKey("integration.id"))

    currency: Mapped["currencies.Currency"] = relationship(
        "Currency", overlaps="source_account, dest_account"
    )
    source_account: Mapped["currencies.Account"] = relationship(
        "Account",
        foreign_keys=[currency_id, source_account_id],
        overlaps="currency, dest_account",
    )
    dest_account: Mapped["currencies.Account"] = relationship(
        "Account",
        foreign_keys=[currency_id, dest_account_id],
        overlaps="currency, source_account",
    )
    integration: Mapped["integrations.Integration"] = relationship()

    __table_args__: Any = (
        ForeignKeyConstraint(
            ["currency_id", "source_account_id"],
            ["account.currency_id", "account.id"],
        ),
        ForeignKeyConstraint(
            ["currency_id", "dest_account_id"],
            ["account.currency_id", "account.id"],
        ),
        {},
    )

    def execute(self, db: Session) -> None:
        # TODO: Maybe add a check to ensure the transaction is pending here?

        src_account = db.execute(
            select(currencies.Account)
            .with_for_update()
            .filter_by(id=self.source_account_id, currency_id=self.currency_id)
        ).scalar()

        dest_account = db.execute(
            select(currencies.Account)
            .with_for_update()
            .filter_by(id=self.dest_account_id, currency_id=self.currency_id)
        ).scalar()

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
        return db.execute(
            select(Transaction).filter_by(id=transaction_id, currency_id=currency_id)
        ).scalar()

    @classmethod
    def get_transactions_for_currency(
        cls, db: Session, currency_id: str
    ) -> Sequence["Transaction"]:
        return (
            db.execute(select(Transaction).filter_by(currency_id=currency_id))
            .scalars()
            .all()
        )
