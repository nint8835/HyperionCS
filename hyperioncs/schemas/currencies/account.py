from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class CreateAccountSchema(BaseModel):
    id: str
    starting_balance: int = 0
    system_account: bool = False
    display_name: Optional[str] = None


class AccountSchema(BaseModel):
    id: str
    currency_id: UUID
    balance: int
    date_created: datetime
    date_modified: datetime
    system_account: bool
    display_name: Optional[str]

    class Config:
        orm_mode = True
