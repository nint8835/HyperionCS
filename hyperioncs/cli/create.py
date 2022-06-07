import jwt
import typer

from hyperioncs.config import config
from hyperioncs.database import SessionLocal
from hyperioncs.models.currencies import Currency
from hyperioncs.models.integrations import Integration, IntegrationConnection

from . import typer_app

create_app = typer.Typer(help="Create Hyperion resources.")
typer_app.add_typer(create_app, name="create")


@create_app.command("currency")
def create_currency(
    owner_id: str = typer.Option(
        ..., help="Discord ID of the user who will own this currency", prompt=True
    ),
    name: str = typer.Option(..., help="Name of this currency", prompt=True),
    singular_form: str = typer.Option(
        ...,
        help="Term for the singular form of this currency (for example, dollar)",
        prompt=True,
    ),
    plural_form: str = typer.Option(
        ...,
        help="Term for the plural form of this currency (for example, dollars)",
        prompt=True,
    ),
    shortcode: str = typer.Option(
        ..., help="Short currency code for this currency", prompt=True
    ),
) -> None:
    """Create a new currency."""
    currency = Currency(
        name=name,
        singular_form=singular_form,
        plural_form=plural_form,
        shortcode=shortcode,
        owner_id=owner_id,
    )
    session = SessionLocal()
    session.add(currency)
    session.commit()

    typer.echo(
        typer.style("Created currency with ID ", fg="green")
        + typer.style(currency.id, fg="yellow")
    )


@create_app.command("integration")
def create_integration(
    name: str = typer.Option(..., help="Name of this integration", prompt=True),
    description: str = typer.Option(
        ..., help="Description of this integration", prompt=True
    ),
    link: str = typer.Option(..., help="Link to this integration", prompt=True),
    public: bool = typer.Option(
        ..., help="Whether this integration is public", prompt=True
    ),
    owner_id: str = typer.Option(
        ..., help="Discord ID of the user who will own this integration", prompt=True
    ),
    official: bool = typer.Option(
        ..., help="Whether this integration is official", prompt=True
    ),
):
    """Create a new integration."""
    integration = Integration(
        name=name,
        description=description,
        link=link,
        public=public,
        owner_id=owner_id,
        official=official,
    )
    session = SessionLocal()
    session.add(integration)
    session.commit()

    typer.echo(
        typer.style("Created integration with ID ", fg="green")
        + typer.style(integration.id, fg="yellow")
    )


@create_app.command("integration-connection")
def create_integration_connection(
    currency_id: str = typer.Option(..., help="ID of the currency", prompt=True),
    integration_id: str = typer.Option(..., help="ID of the integration", prompt=True),
):
    """Create a new integration connection."""
    integration_connection = IntegrationConnection(
        currency_id=currency_id, integration_id=integration_id
    )
    session = SessionLocal()
    session.add(integration_connection)
    session.commit()

    typer.echo(
        typer.style("Created integration connection with ID ", fg="green")
        + typer.style(integration_connection.id, fg="yellow")
    )
    typer.echo(
        typer.style("JWT: ", fg="green")
        + typer.style(
            jwt.encode(
                {"integration_connection_id": str(integration_connection.id)},
                config.jwt_secret_key,
                config.jwt_algorithm,
            ),
            fg="yellow",
        )
    )
