from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from hyperioncs.db import Base
from hyperioncs.db.models.utils import default_uuid_str


class Integration(Base):
    __tablename__ = "integrations"

    id: Mapped[str] = mapped_column(primary_key=True, default=default_uuid_str)
    name: Mapped[str]
    description: Mapped[str]
    url: Mapped[Optional[str]]
    private: Mapped[bool]
