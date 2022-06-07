"""Implement base DB models

Revision ID: 3d4fc62b7bde
Revises: None
Create Date: 2021-05-08 00:37:04.168648

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "3d4fc62b7bde"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "currency",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("singular_form", sa.String(), nullable=False),
        sa.Column("plural_form", sa.String(), nullable=False),
        sa.Column("shortcode", sa.String(), nullable=False),
        sa.Column("owner_id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_currency_name"), "currency", ["name"], unique=True)
    op.create_index(
        op.f("ix_currency_owner_id"), "currency", ["owner_id"], unique=False
    )
    op.create_index(
        op.f("ix_currency_shortcode"), "currency", ["shortcode"], unique=True
    )
    op.create_table(
        "integration",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("official", sa.Boolean(), nullable=False),
        sa.Column("link", sa.String(), nullable=True),
        sa.Column("public", sa.Boolean(), nullable=False),
        sa.Column("owner_id", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_integration_owner_id"), "integration", ["owner_id"], unique=False
    )
    op.create_table(
        "account",
        sa.Column("currency_id", sa.String(), nullable=False),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("balance", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["currency_id"],
            ["currency.id"],
        ),
        sa.PrimaryKeyConstraint("currency_id", "id"),
    )
    op.create_table(
        "integration_connection",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("integration_id", sa.String(), nullable=False),
        sa.Column("currency_id", sa.String(), nullable=False),
        sa.Column("last_used", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["currency_id"],
            ["currency.id"],
        ),
        sa.ForeignKeyConstraint(
            ["integration_id"],
            ["integration.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_integration_connection_currency_id"),
        "integration_connection",
        ["currency_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_integration_connection_integration_id"),
        "integration_connection",
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
        sa.Column("date_created", sa.DateTime(), nullable=False),
        sa.Column("date_modified", sa.DateTime(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("source_currency_id", sa.String(), nullable=True),
        sa.Column("source_account_id", sa.String(), nullable=True),
        sa.Column("dest_currency_id", sa.String(), nullable=True),
        sa.Column("dest_account_id", sa.String(), nullable=True),
        sa.Column("integration_id", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["dest_currency_id", "dest_account_id"],
            ["account.currency_id", "account.id"],
        ),
        sa.ForeignKeyConstraint(
            ["dest_currency_id"],
            ["currency.id"],
        ),
        sa.ForeignKeyConstraint(
            ["integration_id"],
            ["integration.id"],
        ),
        sa.ForeignKeyConstraint(
            ["source_currency_id", "source_account_id"],
            ["account.currency_id", "account.id"],
        ),
        sa.ForeignKeyConstraint(
            ["source_currency_id"],
            ["currency.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_transaction_dest_account_id"),
        "transaction",
        ["dest_account_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_transaction_dest_currency_id"),
        "transaction",
        ["dest_currency_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_transaction_source_account_id"),
        "transaction",
        ["source_account_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_transaction_source_currency_id"),
        "transaction",
        ["source_currency_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_transaction_source_currency_id"), table_name="transaction")
    op.drop_index(op.f("ix_transaction_source_account_id"), table_name="transaction")
    op.drop_index(op.f("ix_transaction_dest_currency_id"), table_name="transaction")
    op.drop_index(op.f("ix_transaction_dest_account_id"), table_name="transaction")
    op.drop_table("transaction")
    op.drop_index(
        op.f("ix_integration_connection_integration_id"),
        table_name="integration_connection",
    )
    op.drop_index(
        op.f("ix_integration_connection_currency_id"),
        table_name="integration_connection",
    )
    op.drop_table("integration_connection")
    op.drop_table("account")
    op.drop_index(op.f("ix_integration_owner_id"), table_name="integration")
    op.drop_table("integration")
    op.drop_index(op.f("ix_currency_shortcode"), table_name="currency")
    op.drop_index(op.f("ix_currency_owner_id"), table_name="currency")
    op.drop_index(op.f("ix_currency_name"), table_name="currency")
    op.drop_table("currency")
