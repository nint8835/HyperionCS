# type: ignore

from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException, Request

from hyperioncs.config import config
from hyperioncs.schemas.user import SessionUser

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


def get_session_user(request: Request) -> SessionUser | None:
    if "user" not in request.session:
        return None

    return SessionUser(**request.session["user"])


def require_session_user(request: Request) -> SessionUser:
    user = get_session_user(request)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="You must be logged in to access this API.",
            headers={"Content-Type": "application/json"},
        )

    return user
