from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from hyperioncs.models.currencies.transactions import TransactionState


class CreateTransactionSchema(BaseModel):
    source_account_id: str
    dest_account_id: str
    amount: int
    description: Optional[str] = None


class CancelTransactionSchema(BaseModel):
    reason: Optional[str] = None


class TransactionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    amount: int
    state: TransactionState
    state_reason: Optional[str] = None
    description: Optional[str] = None
    source_currency_id: UUID
    source_account_id: str
    dest_currency_id: UUID
    dest_account_id: str
    integration_id: UUID
    date_created: datetime
    date_modified: datetime
