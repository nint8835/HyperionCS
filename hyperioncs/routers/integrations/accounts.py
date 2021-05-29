from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from hyperioncs.dependencies import get_db, get_integration
from hyperioncs.models.currencies import Account
from hyperioncs.models.integrations import IntegrationConnection
from hyperioncs.schemas.currencies import AccountSchema, CreateAccountSchema

accounts_router = APIRouter(tags=["Accounts"])


@accounts_router.get("", response_model=List[AccountSchema])
def get_all_accounts(
    integration: IntegrationConnection = Depends(get_integration),
    db: Session = Depends(get_db),
) -> List[Account]:
    """Get details of all accounts for the current currency."""
    return Account.get_accounts_for_currency(db, integration.currency_id)


@accounts_router.get("/{account_id}", response_model=AccountSchema)
def get_account(
    account_id: str,
    integration: IntegrationConnection = Depends(get_integration),
    db: Session = Depends(get_db),
) -> Account:
    """Retrieve details of a single account for the current currency."""
    account = Account.get_account(db, integration.currency_id, account_id)

    if account is None:
        raise HTTPException(404, "Specified account does not exist.")

    return account


@accounts_router.post("", response_model=AccountSchema)
def create_account(
    account: CreateAccountSchema,
    integration: IntegrationConnection = Depends(get_integration),
    db: Session = Depends(get_db),
) -> Account:
    """Create a new account for the current currency."""
    if Account.get_account(db, integration.currency_id, account.id) is not None:
        raise HTTPException(409, "Account with specified ID already exists.")

    new_account = Account(
        id=account.id,
        currency_id=integration.currency_id,
        system_account=account.system_account,
        display_name=account.display_name,
    )
    db.add(new_account)
    db.commit()

    return new_account
