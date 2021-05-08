import typer
import uvicorn

typer_app = typer.Typer(
    help="Manage and run Hyperion Currency System from the command-line."
)


@typer_app.command()
def run() -> None:
    """Start the Hyperion Currency System app."""
    uvicorn.run("hyperioncs:app")
