import uuid
from typing import TYPE_CHECKING, List, Optional, Type, Union

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    and_,
    func,
    select,
    table,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session, column_property, relationship
from sqlalchemy.sql.functions import coalesce

import hyperioncs.models.currencies.transactions as transactions
from hyperioncs.models.base import Base, BaseDBModel

if TYPE_CHECKING:
    from .currency import Currency
    from .transactions import Transaction


class Account(Base, BaseDBModel):
    __tablename__ = "account"

    currency_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("currency.id"), primary_key=True
    )
    id: str = Column(String, primary_key=True)
    balance: int = Column(Integer, nullable=False, default=0)
    system_account: bool = Column(Boolean, default=False, nullable=False)
    display_name: Optional[str] = Column(String)
    effective_balance = column_property(
        balance
        + (
            select(coalesce(func.sum(transactions.Transaction.amount), 0))
            .where(
                transactions.Transaction.state == transactions.TransactionState.PENDING
            )
            .where(transactions.Transaction.dest_account_id == id)
            .where(transactions.Transaction.dest_currency_id == currency_id)
            .scalar_subquery()
        )
        - (
            select(coalesce(func.sum(transactions.Transaction.amount), 0))
            .where(
                transactions.Transaction.state == transactions.TransactionState.PENDING
            )
            .where(transactions.Transaction.source_account_id == id)
            .where(transactions.Transaction.source_currency_id == currency_id)
            .scalar_subquery()
        )
    )

    currency: "Currency" = relationship("Currency")

    @classmethod
    def get_accounts_for_currency(
        cls: Type["Account"], db: Session, currency_id: Union[uuid.UUID, str]
    ) -> List["Account"]:
        return db.query(Account).filter_by(currency_id=currency_id).all()

    @classmethod
    def get_account(
        cls: Type["Account"],
        db: Session,
        currency_id: Union[uuid.UUID, str],
        account_id: str,
    ) -> Optional["Account"]:
        return (
            db.query(Account).filter_by(currency_id=currency_id, id=account_id).first()
        )
