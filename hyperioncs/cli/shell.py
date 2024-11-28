import IPython
from sqlalchemy.orm import Session

from hyperioncs.database import SessionLocal

from . import typer_app


@typer_app.command()
def shell() -> None:
    """Open an interactive Python shell for testing."""

    db: Session = SessionLocal()  # type: ignore # noqa
    IPython.embed()  # type: ignore
