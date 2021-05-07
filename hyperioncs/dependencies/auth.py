from typing import Any, Dict, cast

from authlib.integrations.starlette_client import OAuth
from fastapi import Request
from fastapi.exceptions import HTTPException

from ..config import config

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


def get_current_user(request: Request) -> Dict[Any, Any]:
    if "user" not in request.session:
        raise HTTPException(401, "User not logged in")

    return cast(Dict[Any, Any], request.session["user"])
