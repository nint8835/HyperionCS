from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class IntegrationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: Optional[str] = None
    official: bool
    link: Optional[str] = None
    public: bool
    owner_id: str
    date_created: datetime
    date_modified: datetime
