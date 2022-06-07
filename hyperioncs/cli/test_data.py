import jwt
import typer
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session

from hyperioncs.config import config
from hyperioncs.database import SessionLocal
from hyperioncs.models.currencies import Account, Currency
from hyperioncs.models.integrations import Integration, IntegrationConnection

from . import typer_app

TESTING_DISCORD_ID = "106162668032802816"


@typer_app.command()
def dev_data() -> None:
    """Create development data for testing with."""
    typer.secho("Creating dev data...", fg="cyan")

    session: Session = SessionLocal()

    test_currency = Currency(
        name="Testcoins",
        singular_form="Testcoin",
        plural_form="Testcoins",
        shortcode="TST",
        owner_id=TESTING_DISCORD_ID,
    )
    test_integration = Integration(
        name="Hyperion Test Bot",
        description="A real cool bot for testing. Real good.",
        official=True,
        link="https://github.com/nint8835/hyperion-test-bot",
        public=False,
        owner_id=TESTING_DISCORD_ID,
    )

    session.add(test_currency)
    session.add(test_integration)
    session.flush()

    test_integration_connection = IntegrationConnection(
        integration_id=test_integration.id, currency_id=test_currency.id
    )
    test_account_1 = Account(
        currency_id=test_currency.id, id=TESTING_DISCORD_ID, balance=100
    )
    test_account_2 = Account(
        currency_id=test_currency.id, id="178958252820791296", balance=0
    )
    session.add(test_integration_connection)
    session.add(test_account_1)
    session.add(test_account_2)

    session.commit()

    typer.secho("Dev data created!", fg="green")

    for resource_name, resource in [
        ("Currency", test_currency),
        ("Integration", test_integration),
        ("IntegrationConnection", test_integration_connection),
        ("Account", test_account_1),
        ("Account", test_account_2),
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
