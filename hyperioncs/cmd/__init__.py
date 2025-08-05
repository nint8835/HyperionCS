import typer
import uvicorn

from hyperioncs.config import config

app = typer.Typer()


@app.command()
def start() -> None:
    """Run Hyperion."""

    uvicorn.run(
        "hyperioncs.app:app",
        host=config.bind_host,
        port=config.bind_port,
        proxy_headers=config.behind_reverse_proxy,
        forwarded_allow_ips="*" if config.behind_reverse_proxy else None,
    )


__all__ = ["app"]
