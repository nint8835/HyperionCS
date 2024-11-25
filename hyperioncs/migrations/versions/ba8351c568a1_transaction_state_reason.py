"""Add transaction state reason

Revision ID: ba8351c568a1
Revises: fd56cfad251c
Create Date: 2021-05-21 20:35:55.819666

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "ba8351c568a1"
down_revision = "fd56cfad251c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("transaction", sa.Column("state_reason", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("transaction", "state_reason")
