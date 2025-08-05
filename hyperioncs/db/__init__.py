import enum
import typing

import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from hyperioncs.config import config


class Base(AsyncAttrs, DeclarativeBase):
    type_annotation_map: dict[typing.Any, typing.Any] = {
        enum.Enum: sqlalchemy.Enum(enum.Enum, native_enum=False),
        typing.Literal: sqlalchemy.Enum(enum.Enum, native_enum=False),
    }

    metadata = sqlalchemy.MetaData(
        naming_convention={
            "pk": "pk_%(table_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "ix": "ix_%(table_name)s_%(column_0_name)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
        }
    )


engine = create_async_engine(config.async_db_connection_uri, echo=config.db_log_queries)

async_session = async_sessionmaker(engine, expire_on_commit=False)
