import uuid
from datetime import datetime
from typing import Optional, Type, TypeVar, Union

from sqlalchemy import Column, DateTime
from sqlalchemy.exc import DataError
from sqlalchemy.orm import Mapped, Session, declarative_mixin, declared_attr

from ..database import Base

ModelType = TypeVar("ModelType", bound="BaseDBModel")


@declarative_mixin
class BaseDBModel:
    """Generic model providing base functionality used by all models.

    Must be inherited from in addition to Base.
    """

    @declared_attr
    def date_created(cls) -> Mapped[datetime]:
        return Column(DateTime, nullable=False, default=datetime.utcnow)

    @declared_attr
    def date_modified(cls) -> Mapped[datetime]:
        return Column(DateTime, nullable=False, default=datetime.utcnow)

    @classmethod
    def get_by_id(
        cls: Type[ModelType], session: Session, id: Union[uuid.UUID, str]
    ) -> Optional[ModelType]:
        try:
            return session.query(cls).filter_by(id=id).first()
        except DataError:
            return None


__all__ = ["Base", "BaseDBModel"]
