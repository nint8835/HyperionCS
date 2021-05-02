from sqlalchemy import Column, Integer

from ..database import Base


class TestModel(Base):
    __tablename__ = "test"

    id = Column(Integer, primary_key=True)
