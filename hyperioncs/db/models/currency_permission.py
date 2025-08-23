import enum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hyperioncs.db import Base
from hyperioncs.db.models.utils import default_uuid_str

if TYPE_CHECKING:
    from .currency import Currency


class CurrencyRole(enum.Enum):
    Owner = "owner"


class CurrencyActionRoles:
    Edit = [CurrencyRole.Owner]


class CurrencyPermission(Base):
    __tablename__ = "currency_permissions"

    id: Mapped[str] = mapped_column(primary_key=True, default=default_uuid_str)
    user_id: Mapped[str]
    currency_shortcode: Mapped[str] = mapped_column(
        ForeignKey("currencies.shortcode", ondelete="CASCADE")
    )
    currency: Mapped["Currency"] = relationship(lazy="raise")

    role: Mapped[CurrencyRole]
