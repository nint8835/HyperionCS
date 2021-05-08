import jwt
import typer
from alembic import command
from alembic.config import Config
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session

from ..config import config
from ..database import SessionLocal
from ..models.currencies import Account, Currency
from ..models.integrations import Integration, IntegrationConnection
from . import typer_app

TESTING_DISCORD_ID = "106162668032802816"


@typer_app.command()
def wipe_db(
    migrate: bool = typer.Option(
        True,
        help="Apply all database migrations to restore the database to a ready state.",
    )
) -> None:
    """Empty the contents of the development database."""
    typer.secho("Wiping DB...", fg="yellow")

    session: Session = SessionLocal()
    session.execute("DROP SCHEMA public CASCADE")
    session.execute("CREATE SCHEMA public")
    session.commit()

    if migrate:
        typer.secho("Upgrading DB...", fg="yellow")
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")

    typer.secho("DB ready!", fg="green")


@typer_app.command()
def dev_data() -> None:
    """Create development data for testing with."""
    typer.secho("Creating test data...", fg="cyan")

    session: Session = SessionLocal()

    test_currency = Currency(
        name="Testcoins",
        singular_form="Testcoin",
        plural_form="Testcoins",
        shortcode="TST",
        owner_id=TESTING_DISCORD_ID,
    )
    test_integration = Integration(
        name="Testing integration",
        description="A real cool integration for testing. Real good.",
        official=True,
        link=None,
        public=True,
        owner_id=TESTING_DISCORD_ID,
    )

    session.add(test_currency)
    session.add(test_integration)
    session.flush()

    test_integration_connection = IntegrationConnection(
        integration_id=test_integration.id, currency_id=test_currency.id
    )
    test_account = Account(
        currency_id=test_currency.id, id=TESTING_DISCORD_ID, balance=100
    )
    session.add(test_integration_connection)
    session.add(test_account)

    session.commit()

    typer.secho("Test data created!", fg="green")

    for resource_name, resource in [
        ("Currency", test_currency),
        ("Integration", test_integration),
        ("IntegrationConnection", test_integration_connection),
        ("Account", test_account),
    ]:
        typer.echo(
            typer.style(f"{resource_name}: ", fg="green")
            + typer.style(", ".join(map(str, inspect(resource).identity)), fg="yellow")
        )
        if isinstance(resource, IntegrationConnection):
            typer.echo(
                typer.style("  JWT: ", fg="green")
                + typer.style(
                    jwt.encode(
                        {"integration_connection_id": str(resource.id)},
                        config.jwt_secret_key,
                        config.jwt_algorithm,
                    )
                )
            )
