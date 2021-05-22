"""Add extra account fields

Revision ID: 73516abc4ea3
Revises: ba8351c568a1
Create Date: 2021-05-21 22:02:00.571842

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "73516abc4ea3"
down_revision = "ba8351c568a1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("account", sa.Column("system_account", sa.Boolean(), nullable=True))
    op.execute("UPDATE account SET system_account = false")
    op.alter_column("account", "system_account", nullable=True)
    op.add_column("account", sa.Column("display_name", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("account", "display_name")
    op.drop_column("account", "system_account")
