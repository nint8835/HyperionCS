from datetime import datetime

from sqlalchemy import Column, DateTime

from ..database import Base


class GenericModel:
    """Generic model providing base functionality used by all models.

    Must be inherited from in addition to Base.
    """

    date_created = Column(DateTime, nullable=False, default=datetime.utcnow)
    date_modified = Column(DateTime, nullable=False, default=datetime.utcnow)


__all__ = ["Base", "GenericModel"]
