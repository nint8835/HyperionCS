from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class IntegrationConnectionSchema(BaseModel):
    id: UUID
    integration_id: UUID
    currency_id: UUID
    last_used: datetime
    date_created: datetime
    date_modified: datetime

    class Config:
        orm_mode = True
