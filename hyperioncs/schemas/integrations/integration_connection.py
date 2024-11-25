from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class IntegrationConnectionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    integration_id: UUID
    currency_id: UUID
    last_used: datetime
    date_created: datetime
    date_modified: datetime
