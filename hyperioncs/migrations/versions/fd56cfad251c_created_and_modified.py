"""Add date_modified and date_created to all models

Revision ID: fd56cfad251c
Revises: 3d4fc62b7bde
Create Date: 2021-05-08 03:07:45.994627

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "fd56cfad251c"
down_revision = "3d4fc62b7bde"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("account", sa.Column("date_created", sa.DateTime(), nullable=False))
    op.add_column("account", sa.Column("date_modified", sa.DateTime(), nullable=False))
    op.add_column("currency", sa.Column("date_created", sa.DateTime(), nullable=False))
    op.add_column("currency", sa.Column("date_modified", sa.DateTime(), nullable=False))
    op.add_column(
        "integration", sa.Column("date_created", sa.DateTime(), nullable=False)
    )
    op.add_column(
        "integration", sa.Column("date_modified", sa.DateTime(), nullable=False)
    )
    op.add_column(
        "integration_connection",
        sa.Column("date_created", sa.DateTime(), nullable=False),
    )
    op.add_column(
        "integration_connection",
        sa.Column("date_modified", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("integration_connection", "date_modified")
    op.drop_column("integration_connection", "date_created")
    op.drop_column("integration", "date_modified")
    op.drop_column("integration", "date_created")
    op.drop_column("currency", "date_modified")
    op.drop_column("currency", "date_created")
    op.drop_column("account", "date_modified")
    op.drop_column("account", "date_created")
