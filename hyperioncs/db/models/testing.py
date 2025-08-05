from sqlalchemy.orm import Mapped, mapped_column

from hyperioncs.db import Base


class TestModel(Base):
    __tablename__ = "test_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
