from typing import Optional

from sqlalchemy import Boolean, Column, String

from hyperioncs.models.base import Base, BaseDBModel
from hyperioncs.models.utils import default_uuid_str


class Integration(Base, BaseDBModel):
    __tablename__ = "integration"

    id: str = Column(String, primary_key=True, default=default_uuid_str)
    name: str = Column(String, nullable=False)
    description: Optional[str] = Column(String)
    official: bool = Column(Boolean, nullable=False, default=False)
    link: Optional[str] = Column(String)
    public: bool = Column(Boolean, nullable=False, default=False)
    owner_id: str = Column(String, index=True)
