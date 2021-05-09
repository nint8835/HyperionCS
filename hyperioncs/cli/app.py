import typer
import uvicorn

typer_app = typer.Typer(
    help="Manage and run Hyperion Currency System from the command-line."
)


@typer_app.command()
def run(port: int = typer.Option(8000, help="Port the app should listen on.")) -> None:
    """Start the Hyperion Currency System app."""
    uvicorn.run("hyperioncs:app", port=port)
