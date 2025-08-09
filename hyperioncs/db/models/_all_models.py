# ruff: noqa: F401
# pyright: reportUnusedImport=false

# Utility file to ensure all models are imported for Alembic auto-generation.
# Should not be imported outside of hyperioncs.migrations.env

from .currency import Currency
from .permission import Permission
