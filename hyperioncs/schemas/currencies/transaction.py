from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from ...models.currencies.transactions import TransactionState


class CreateTransactionSchema(BaseModel):
    source_account_id: str
    dest_account_id: str
    amount: int
    description: Optional[str] = None


class TransactionSchema(BaseModel):
    id: UUID
    amount: int
    state: TransactionState
    state_reason: Optional[str]
    description: Optional[str]
    source_currency_id: UUID
    source_account_id: str
    dest_currency_id: UUID
    dest_account_id: str
    integration_id: UUID
    date_created: datetime
    date_modified: datetime

    class Config:
        orm_mode = True
