from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CreateAccountSchema(BaseModel):
    id: str
    system_account: bool = False
    display_name: Optional[str] = None


class AccountSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    currency_id: UUID
    balance: int
    effective_balance: int
    date_created: datetime
    date_modified: datetime
    system_account: bool
    display_name: Optional[str] = None
