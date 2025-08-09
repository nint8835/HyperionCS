from sqlalchemy.orm import Mapped, mapped_column

from hyperioncs.db import Base


class Currency(Base):
    __tablename__ = "currencies"

    shortcode: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    singular_form: Mapped[str]
    plural_form: Mapped[str]
