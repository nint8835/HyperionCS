"""Initial migration

Revision ID: 0522338e0df4
Revises:
Create Date: 2025-08-23 11:31:43.340234

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0522338e0df4"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "currencies",
        sa.Column("shortcode", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("singular_form", sa.String(), nullable=False),
        sa.Column("plural_form", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("shortcode", name=op.f("pk_currencies")),
    )
    op.create_table(
        "currency_permissions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("currency_shortcode", sa.String(), nullable=False),
        sa.Column(
            "role",
            sa.Enum("Owner", name="currencyrole", native_enum=False),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["currency_shortcode"],
            ["currencies.shortcode"],
            name=op.f("fk_currency_permissions_currency_shortcode_currencies"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_currency_permissions")),
    )


def downgrade() -> None:
    op.drop_table("currency_permissions")
    op.drop_table("currencies")
