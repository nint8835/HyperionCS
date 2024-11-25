from typing import List, Optional, Type, cast

from sqlalchemy import ForeignKey, func, select
from sqlalchemy.orm import Mapped, Session, column_property, mapped_column, relationship
from sqlalchemy.sql.functions import coalesce

import hyperioncs.models.currencies as currencies
import hyperioncs.models.currencies.transactions as transactions
from hyperioncs.models.base import Base, BaseDBModel


class Account(Base, BaseDBModel):
    __tablename__ = "account"

    currency_id: Mapped[str] = mapped_column(
        ForeignKey("currency.id"), primary_key=True
    )
    id: Mapped[str] = mapped_column(primary_key=True)
    balance: Mapped[int] = mapped_column(default=0)
    system_account: Mapped[Optional[bool]] = mapped_column(default=False)
    display_name: Mapped[Optional[str]]
    effective_balance = cast(
        int,
        column_property(
            balance
            + (
                select(coalesce(func.sum(transactions.Transaction.amount), 0))
                .where(
                    transactions.Transaction.state
                    == transactions.TransactionState.PENDING
                )
                .where(transactions.Transaction.dest_account_id == id)
                .where(transactions.Transaction.dest_currency_id == currency_id)
                .scalar_subquery()
            )
            - (
                select(coalesce(func.sum(transactions.Transaction.amount), 0))
                .where(
                    transactions.Transaction.state
                    == transactions.TransactionState.PENDING
                )
                .where(transactions.Transaction.source_account_id == id)
                .where(transactions.Transaction.source_currency_id == currency_id)
                .scalar_subquery()
            )
        ),
    )

    currency: Mapped["currencies.Currency"] = relationship()

    @classmethod
    def get_accounts_for_currency(
        cls: Type["Account"], db: Session, currency_id: str
    ) -> List["Account"]:
        return db.query(Account).filter_by(currency_id=currency_id).all()

    @classmethod
    def get_account(
        cls: Type["Account"],
        db: Session,
        currency_id: str,
        account_id: str,
    ) -> Optional["Account"]:
        return (
            db.query(Account).filter_by(currency_id=currency_id, id=account_id).first()
        )
