from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CurrencySchema(BaseModel):
    id: UUID
    name: str
    singular_form: str
    plural_form: str
    shortcode: str
    owner_id: str
    date_created: datetime
    date_modified: datetime

    class Config:
        orm_mode = True
