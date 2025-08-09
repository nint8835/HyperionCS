import enum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hyperioncs.db import Base
from hyperioncs.db.models.utils import default_uuid_str

if TYPE_CHECKING:
    from .currency import Currency


class PermissionRole(enum.Enum):
    # User roles
    Owner = "owner"


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[str] = mapped_column(primary_key=True, default=default_uuid_str)

    # Permission owners
    user_id: Mapped[str | None] = mapped_column(default=None)

    # Target resource
    currency_shortcode: Mapped[str | None] = mapped_column(
        ForeignKey("currencies.shortcode", ondelete="CASCADE"), default=None
    )
    currency: Mapped["Currency | None"] = relationship(lazy="raise")

    role: Mapped[PermissionRole]
