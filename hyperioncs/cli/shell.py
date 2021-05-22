import IPython
from sqlalchemy.orm import Session

from ..database import SessionLocal
from . import typer_app


@typer_app.command()
def shell() -> None:
    """Open an interactive Python shell for testing."""

    db: Session = SessionLocal()  # noqa
    IPython.embed()
