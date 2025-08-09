"""Initial currencies table

Revision ID: d59e08077330
Revises:
Create Date: 2025-08-09 17:27:25.554598

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d59e08077330"
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
        "permissions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=True),
        sa.Column("currency_shortcode", sa.String(), nullable=True),
        sa.Column(
            "role",
            sa.Enum("Owner", name="permissionrole", native_enum=False),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["currency_shortcode"],
            ["currencies.shortcode"],
            name=op.f("fk_permissions_currency_shortcode_currencies"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_permissions")),
    )


def downgrade() -> None:
    op.drop_table("permissions")
    op.drop_table("currencies")
