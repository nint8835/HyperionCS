# type: ignore

from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException, Request

from hyperioncs.api.app.schemas.user import DiscordUser
from hyperioncs.config import config

oauth = OAuth()
oauth.register(
    "discord",
    client_id=config.client_id,
    client_secret=config.client_secret,
    api_base_url="https://discord.com/api/",
    access_token_url="https://discord.com/api/oauth2/token",
    authorize_url="https://discord.com/api/oauth2/authorize",
    client_kwargs={
        "token_endpoint_auth_method": "client_secret_post",
        "scope": "identify",
    },
)


def get_discord_user(request: Request) -> DiscordUser | None:
    if "user" not in request.session:
        return None

    return DiscordUser(**request.session["user"])


def require_discord_user(request: Request) -> DiscordUser:
    user = get_discord_user(request)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="You must be logged in to access this API.",
            headers={"Content-Type": "application/json"},
        )

    return user
