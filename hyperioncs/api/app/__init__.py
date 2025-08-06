from typing import TypedDict

from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import Response
from starlette.types import Scope

from hyperioncs.config import config


class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope: Scope) -> Response:
        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code == 404:
                return await super().get_response("index.html", scope)
            else:
                raise exc


def generate_unique_id(route: APIRoute) -> str:
    return route.name


# Needed to prevent type issues applying kwargs to FastAPI. Really wish Python's type system could handle this.
class FastAPIKwargs(TypedDict, total=False):
    docs_url: str | None
    redoc_url: str | None
    openapi_url: str | None


app_kwargs: FastAPIKwargs = (
    {"docs_url": None, "redoc_url": None, "openapi_url": None}
    if config.is_production
    else {}
)
main_app = FastAPI(
    title="Hyperion Web App",
    generate_unique_id_function=generate_unique_id,
    **app_kwargs,
)


class PlaceholderSchema(BaseModel):
    message: str = "This is a placeholder endpoint to ensure OpenAPI code generation works correctly."


@main_app.get("/placeholder", response_model=PlaceholderSchema)
async def placeholder_endpoint() -> PlaceholderSchema:
    return PlaceholderSchema()


main_app.add_middleware(SessionMiddleware, secret_key=config.session_secret)

main_app.mount("/", SPAStaticFiles(directory="frontend/dist", html=True), "frontend")
