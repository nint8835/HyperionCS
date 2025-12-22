from contextlib import asynccontextmanager

from starlette.applications import Starlette
from starlette.middleware.sessions import SessionMiddleware
from starlette.routing import Mount

from hyperioncs.api.app import main_app
from hyperioncs.api.integrations.v1 import integrations_api_v1
from hyperioncs.config import config
from hyperioncs.db import engine as db_engine


@asynccontextmanager
async def starlette_lifespan(app: Starlette):
    yield
    # Dispose of the DB engine on shutdown
    # This is needed to prevent aiosqlite from causing the main thread to hang on shutdown
    # https://github.com/omnilib/aiosqlite/issues/369
    # https://github.com/sqlalchemy/sqlalchemy/issues/13039
    await db_engine.dispose()


app = Starlette(
    routes=[
        Mount("/api/v1", integrations_api_v1),
        Mount("/", main_app),
    ],
    lifespan=starlette_lifespan,
)

app.add_middleware(SessionMiddleware, secret_key=config.session_secret)
