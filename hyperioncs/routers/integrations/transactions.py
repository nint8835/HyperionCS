from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from hyperioncs.dependencies import get_db, get_integration
from hyperioncs.models.currencies import Account
from hyperioncs.models.currencies.transactions import Transaction, TransactionState
from hyperioncs.models.integrations import IntegrationConnection
from hyperioncs.schemas.currencies import CreateTransactionSchema, TransactionSchema

transaction_router = APIRouter(tags=["Transactions"])


@transaction_router.get("", response_model=List[TransactionSchema])
def get_all_transactions(
    integration: IntegrationConnection = Depends(get_integration),
    db: Session = Depends(get_db),
) -> List[Transaction]:
    """Get details of all transactions for the current currency."""
    return Transaction.get_transactions_for_currency(db, integration.currency_id)


@transaction_router.post("", response_model=TransactionSchema)
def create_transaction(
    transaction: CreateTransactionSchema,
    integration: IntegrationConnection = Depends(get_integration),
    db: Session = Depends(get_db),
) -> Transaction:
    """Create a new transaction for the current currency."""
    if (
        Account.get_account(db, integration.currency_id, transaction.source_account_id)
        is None
    ):
        raise HTTPException(409, "Specified source account does not exist.")

    if (
        Account.get_account(db, integration.currency_id, transaction.dest_account_id)
        is None
    ):
        raise HTTPException(409, "Specified destination account does not exist.")

    new_transaction = Transaction(
        source_currency_id=integration.currency_id,
        dest_currency_id=integration.currency_id,
        source_account_id=transaction.source_account_id,
        dest_account_id=transaction.dest_account_id,
        amount=transaction.amount,
        description=transaction.description,
        integration_id=integration.integration_id,
    )
    db.add(new_transaction)
    db.commit()

    return new_transaction


@transaction_router.post("/{transaction_id}/execute", response_model=TransactionSchema)
def execute_transaction(
    transaction_id: str,
    integration: IntegrationConnection = Depends(get_integration),
    db: Session = Depends(get_db),
) -> Transaction:
    transaction = Transaction.get_transaction(
        db, integration.currency_id, transaction_id
    )

    if transaction is None:
        raise HTTPException(
            403,
            "Specified transaction does not exist or you do not have permission to access it.",
        )

    if transaction.state != TransactionState.PENDING:
        raise HTTPException(409, "Cannot execute an already executed transaction.")

    transaction.execute(db)

    return transaction
