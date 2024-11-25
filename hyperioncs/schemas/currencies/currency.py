from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CurrencySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    singular_form: str
    plural_form: str
    shortcode: str
    owner_id: str
    date_created: datetime
    date_modified: datetime
