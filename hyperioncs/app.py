from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from .config import config
from .routers.integrations import accounts_router, integration_router
from .routers.internal import auth_router, index_router

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=config.secret_key)

app.include_router(auth_router)
app.include_router(index_router)

app.include_router(integration_router, prefix="/api/v1/integration")
app.include_router(accounts_router, prefix="/api/v1/accounts")

app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")
templates = Jinja2Templates(directory="frontend/build")


@app.get("/{rest_of_path:path}", include_in_schema=False)
async def serve_frontend(request: Request, rest_of_path: str) -> Response:
    return templates.TemplateResponse("index.html", {"request": request})
