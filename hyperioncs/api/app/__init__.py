from typing import TypedDict

from fastapi import FastAPI

from hyperioncs.config import config


# Needed to prevent type issues applying kwargs to FastAPI. Really with Python's type system could handle this.
class FastAPIKwargs(TypedDict, total=False):
    docs_url: str | None
    redoc_url: str | None
    openapi_url: str | None


app_kwargs: FastAPIKwargs = (
    {"docs_url": None, "redoc_url": None, "openapi_url": None}
    if config.is_production
    else {}
)
main_app = FastAPI(title="Hyperion Web App", **app_kwargs)

__all__ = ["main_app"]
