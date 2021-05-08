import uuid
from datetime import datetime
from typing import Optional, Type, TypeVar, Union

from sqlalchemy import Column, DateTime
from sqlalchemy.exc import DataError
from sqlalchemy.orm import Session

from ..database import Base

ModelType = TypeVar("ModelType", bound="BaseDBModel")


class BaseDBModel:
    """Generic model providing base functionality used by all models.

    Must be inherited from in addition to Base.
    """

    date_created = Column(DateTime, nullable=False, default=datetime.utcnow)
    date_modified = Column(DateTime, nullable=False, default=datetime.utcnow)

    @classmethod
    def get_by_id(
        cls: Type[ModelType], session: Session, id: Union[uuid.UUID, str]
    ) -> Optional[ModelType]:
        try:
            return session.query(cls).filter_by(id=id).first()
        except DataError:
            return None


__all__ = ["Base", "BaseDBModel"]
