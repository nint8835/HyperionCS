"""Create integration token model

Revision ID: 781cb27e06c3
Revises: 97118cf7629a
Create Date: 2025-12-29 18:03:43.785881

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "781cb27e06c3"
down_revision: Union[str, Sequence[str], None] = "97118cf7629a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "integration_tokens",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("integration_id", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["integration_id"],
            ["integrations.id"],
            name=op.f("fk_integration_tokens_integration_id_integrations"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_integration_tokens")),
    )


def downgrade() -> None:
    op.drop_table("integration_tokens")
