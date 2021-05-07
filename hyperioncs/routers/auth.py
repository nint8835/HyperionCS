from typing import cast

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Request
from starlette.responses import RedirectResponse, Response

from ..config import config

auth_router = APIRouter()

oauth = OAuth()
oauth.register(
    "discord",
    client_id=config.discord_client_id,
    client_secret=config.discord_client_secret,
    api_base_url="https://discord.com/api/",
    access_token_url="https://discord.com/api/oauth2/token",
    authorize_url="https://discord.com/api/oauth2/authorize",
    client_kwargs={
        "token_endpoint_auth_method": "client_secret_post",
        "scope": "identify email",
    },
)


@auth_router.route("/login")
async def login(request: Request) -> Response:
    redirect_uri = request.url_for("auth")
    return cast(Response, await oauth.discord.authorize_redirect(request, redirect_uri))


@auth_router.route("/auth")
async def auth(request: Request) -> Response:
    token = await oauth.discord.authorize_access_token(request)
    url = "users/@me"
    resp = await oauth.discord.get(url, token=token)
    user = resp.json()
    request.session["user"] = dict(user)
    return RedirectResponse(url="/")


@auth_router.route("/logout")
async def logout(request: Request) -> Response:
    request.session.pop("user", None)
    return RedirectResponse(url="/")
