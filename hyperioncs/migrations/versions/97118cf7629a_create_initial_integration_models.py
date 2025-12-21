"""Create initial integration models

Revision ID: 97118cf7629a
Revises: 0522338e0df4
Create Date: 2025-12-21 18:59:00.816227

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "97118cf7629a"
down_revision: Union[str, Sequence[str], None] = "0522338e0df4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "integrations",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("url", sa.String(), nullable=True),
        sa.Column("private", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_integrations")),
    )
    op.create_table(
        "integration_connections",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("integration_id", sa.String(), nullable=False),
        sa.Column("currency_shortcode", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["currency_shortcode"],
            ["currencies.shortcode"],
            name=op.f("fk_integration_connections_currency_shortcode_currencies"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["integration_id"],
            ["integrations.id"],
            name=op.f("fk_integration_connections_integration_id_integrations"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_integration_connections")),
    )
    op.create_table(
        "integration_permissions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("integration_id", sa.String(), nullable=False),
        sa.Column(
            "role",
            sa.Enum("Owner", name="integrationrole", native_enum=False),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["integration_id"],
            ["integrations.id"],
            name=op.f("fk_integration_permissions_integration_id_integrations"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_integration_permissions")),
    )


def downgrade() -> None:
    op.drop_table("integration_permissions")
    op.drop_table("integration_connections")
    op.drop_table("integrations")
