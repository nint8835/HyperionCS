from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CreateAccountSchema(BaseModel):
    id: str
    starting_balance: int = 0


class AccountSchema(BaseModel):
    id: str
    currency_id: UUID
    balance: int
    date_created: datetime
    date_modified: datetime

    class Config:
        orm_mode = True
