"""Initial migration

Revision ID: ed28da7f2cfc
Revises:
Create Date: 2024-11-28 22:03:52.529608

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "ed28da7f2cfc"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "currency",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("singular_form", sa.String(), nullable=False),
        sa.Column("plural_form", sa.String(), nullable=False),
        sa.Column("shortcode", sa.String(), nullable=False),
        sa.Column("owner_id", sa.String(), nullable=False),
        sa.Column("date_created", sa.DateTime(), nullable=False),
        sa.Column("date_modified", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_currency")),
    )
    with op.batch_alter_table("currency", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_currency_name"), ["name"], unique=True)
        batch_op.create_index(
            batch_op.f("ix_currency_owner_id"), ["owner_id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_currency_shortcode"), ["shortcode"], unique=True
        )

    op.create_table(
        "integration",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("official", sa.Boolean(), nullable=False),
        sa.Column("public", sa.Boolean(), nullable=False),
        sa.Column("link", sa.String(), nullable=True),
        sa.Column("owner_id", sa.String(), nullable=True),
        sa.Column("date_created", sa.DateTime(), nullable=False),
        sa.Column("date_modified", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_integration")),
    )
    with op.batch_alter_table("integration", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_integration_owner_id"), ["owner_id"], unique=False
        )

    op.create_table(
        "account",
        sa.Column("currency_id", sa.String(), nullable=False),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("balance", sa.Integer(), nullable=False),
        sa.Column("system_account", sa.Boolean(), nullable=True),
        sa.Column("display_name", sa.String(), nullable=True),
        sa.Column("date_created", sa.DateTime(), nullable=False),
        sa.Column("date_modified", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["currency_id"],
            ["currency.id"],
            name=op.f("fk_account_currency_id_currency"),
        ),
        sa.PrimaryKeyConstraint("currency_id", "id", name=op.f("pk_account")),
    )
    op.create_table(
        "integration_connection",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("integration_id", sa.String(), nullable=False),
        sa.Column("currency_id", sa.String(), nullable=False),
        sa.Column("last_used", sa.DateTime(), nullable=True),
        sa.Column("date_created", sa.DateTime(), nullable=False),
        sa.Column("date_modified", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["currency_id"],
            ["currency.id"],
            name=op.f("fk_integration_connection_currency_id_currency"),
        ),
        sa.ForeignKeyConstraint(
            ["integration_id"],
            ["integration.id"],
            name=op.f("fk_integration_connection_integration_id_integration"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_integration_connection")),
    )
    with op.batch_alter_table("integration_connection", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_integration_connection_currency_id"),
            ["currency_id"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_integration_connection_integration_id"),
            ["integration_id"],
            unique=False,
        )

    op.create_table(
        "transaction",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column(
            "state",
            sa.Enum(
                "PENDING",
                "COMPLETE",
                "FAILED",
                "CANCELLED",
                "REVERTED",
                name="transactionstate",
            ),
            nullable=False,
        ),
        sa.Column("state_reason", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("currency_id", sa.String(), nullable=False),
        sa.Column("source_account_id", sa.String(), nullable=True),
        sa.Column("dest_account_id", sa.String(), nullable=True),
        sa.Column("integration_id", sa.String(), nullable=True),
        sa.Column("date_created", sa.DateTime(), nullable=False),
        sa.Column("date_modified", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["currency_id", "dest_account_id"],
            ["account.currency_id", "account.id"],
            name=op.f("fk_transaction_currency_id_account"),
        ),
        sa.ForeignKeyConstraint(
            ["currency_id", "source_account_id"],
            ["account.currency_id", "account.id"],
            name=op.f("fk_transaction_currency_id_account"),
        ),
        sa.ForeignKeyConstraint(
            ["currency_id"],
            ["currency.id"],
            name=op.f("fk_transaction_currency_id_currency"),
        ),
        sa.ForeignKeyConstraint(
            ["integration_id"],
            ["integration.id"],
            name=op.f("fk_transaction_integration_id_integration"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_transaction")),
    )
    with op.batch_alter_table("transaction", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_transaction_currency_id"), ["currency_id"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_transaction_dest_account_id"),
            ["dest_account_id"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_transaction_source_account_id"),
            ["source_account_id"],
            unique=False,
        )


def downgrade():
    with op.batch_alter_table("transaction", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_transaction_source_account_id"))
        batch_op.drop_index(batch_op.f("ix_transaction_dest_account_id"))
        batch_op.drop_index(batch_op.f("ix_transaction_currency_id"))

    op.drop_table("transaction")
    with op.batch_alter_table("integration_connection", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_integration_connection_integration_id"))
        batch_op.drop_index(batch_op.f("ix_integration_connection_currency_id"))

    op.drop_table("integration_connection")
    op.drop_table("account")
    with op.batch_alter_table("integration", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_integration_owner_id"))

    op.drop_table("integration")
    with op.batch_alter_table("currency", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_currency_shortcode"))
        batch_op.drop_index(batch_op.f("ix_currency_owner_id"))
        batch_op.drop_index(batch_op.f("ix_currency_name"))

    op.drop_table("currency")
