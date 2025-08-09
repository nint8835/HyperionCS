# type: ignore

from typing import cast

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse

from hyperioncs.api.app.dependencies.auth import get_discord_user, oauth
from hyperioncs.api.app.schemas.user import DiscordUser

auth_router = APIRouter(tags=["Auth"])


@auth_router.get("/login", include_in_schema=False)
async def login(request: Request) -> Response:
    next_url = request.query_params.get("next", "/")
    request.session["next_url"] = next_url

    redirect_uri = request.url_for("oauth_callback")
    return cast(Response, await oauth.discord.authorize_redirect(request, redirect_uri))


@auth_router.get("/callback", include_in_schema=False)
async def oauth_callback(request: Request) -> Response:
    token = await oauth.discord.authorize_access_token(request)

    user_resp = await oauth.discord.get("users/@me", token=token)
    user = user_resp.json()
    request.session["user"] = DiscordUser(**user).model_dump()

    next_url = request.session.pop("next_url", "/")

    return RedirectResponse(url=next_url)


@auth_router.route("/logout", include_in_schema=False)
async def logout(request: Request) -> Response:
    request.session.pop("user", None)
    return RedirectResponse(url="/")


@auth_router.get("/me")
async def get_current_user(
    user: DiscordUser | None = Depends(get_discord_user),
) -> DiscordUser | None:
    """Retrieve the details of the current user."""
    return user
