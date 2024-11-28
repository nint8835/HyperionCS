from datetime import datetime, timezone
from typing import Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.exc import DataError
from sqlalchemy.orm import Mapped, Session, mapped_column

from hyperioncs.database import Base

ModelType = TypeVar("ModelType", bound="BaseDBModel")


class BaseDBModel:
    """Generic model providing base functionality used by all models.

    Must be inherited from in addition to Base.
    """

    date_created: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    date_modified: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    @classmethod
    def get_by_id(
        cls: Type[ModelType], session: Session, id: str
    ) -> Optional[ModelType]:
        try:
            return session.execute(select(cls).filter_by(id=id)).scalar()
        # TODO: Why am I doing this?
        except DataError:
            return None

    def set_modified(self) -> None:
        self.date_modified = datetime.now(timezone.utc)


__all__ = ["Base", "BaseDBModel"]
