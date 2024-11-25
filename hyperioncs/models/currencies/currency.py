from sqlalchemy import Column, String

from hyperioncs.models.base import Base, BaseDBModel
from hyperioncs.models.utils import default_uuid_str


class Currency(Base, BaseDBModel):
    __tablename__ = "currency"

    id: str = Column(String, primary_key=True, default=default_uuid_str)
    name: str = Column(String, unique=True, index=True, nullable=False)
    singular_form: str = Column(String, nullable=False)
    plural_form: str = Column(String, nullable=False)
    shortcode: str = Column(String, unique=True, index=True, nullable=False)
    owner_id: str = Column(String, index=True, nullable=False)
