from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from hyperioncs.models.base import Base, BaseDBModel
from hyperioncs.models.utils import default_uuid_str


class Integration(Base, BaseDBModel):
    __tablename__ = "integration"

    id: Mapped[str] = mapped_column(primary_key=True, default=default_uuid_str)
    name: Mapped[str]
    description: Mapped[Optional[str]]
    official: Mapped[bool] = mapped_column(default=False)
    public: Mapped[bool] = mapped_column(default=False)
    link: Mapped[Optional[str]]
    owner_id: Mapped[Optional[str]] = mapped_column(index=True)
