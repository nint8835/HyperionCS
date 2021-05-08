from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class IntegrationSchema(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    official: bool
    link: Optional[str]
    public: bool
    owner_id: str
    date_created: datetime
    date_modified: datetime

    class Config:
        orm_mode = True
