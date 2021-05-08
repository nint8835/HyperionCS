from typing import cast

from fastapi import APIRouter, Request
from starlette.responses import RedirectResponse, Response

from ...dependencies.auth import oauth

auth_router = APIRouter()


@auth_router.route("/login")
async def login(request: Request) -> Response:
    redirect_uri = request.url_for("callback")
    return cast(Response, await oauth.discord.authorize_redirect(request, redirect_uri))


@auth_router.route("/callback")
async def callback(request: Request) -> Response:
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
