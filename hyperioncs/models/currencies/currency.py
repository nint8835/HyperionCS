from sqlalchemy.orm import Mapped, mapped_column

from hyperioncs.models.base import Base, BaseDBModel
from hyperioncs.models.utils import default_uuid_str


class Currency(Base, BaseDBModel):
    __tablename__ = "currency"

    id: Mapped[str] = mapped_column(primary_key=True, default=default_uuid_str)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    singular_form: Mapped[str]
    plural_form: Mapped[str]
    shortcode: Mapped[str] = mapped_column(unique=True, index=True)
    owner_id: Mapped[str] = mapped_column(index=True)
