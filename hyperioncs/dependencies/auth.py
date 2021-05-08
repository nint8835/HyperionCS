from datetime import datetime
from typing import Optional

import jwt
from authlib.integrations.starlette_client import OAuth
from fastapi import Depends, Request
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ..config import config
from ..models.integrations import IntegrationConnection
from ..schemas import DiscordUser
from .database import get_db

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


def get_discord_user(request: Request) -> DiscordUser:
    if "user" not in request.session:
        raise HTTPException(401, "User not logged in")

    return DiscordUser(**request.session["user"])


class JWTBearer(HTTPBearer):
    async def __call__(
        self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
        credentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token.")
            return credentials
        else:
            raise HTTPException(status_code=401, detail="No credentials provided.")

    def verify_jwt(self, given_jwt: str) -> bool:
        try:
            decoded_token = jwt.decode(
                given_jwt, config.jwt_secret_key, algorithms=[config.jwt_algorithm]
            )
            if "integration_connection_id" in decoded_token:
                return True
            return False
        except jwt.DecodeError:
            return False


def get_integration(
    request: Request,
    db: Session = Depends(get_db),
    jwt_creds: HTTPAuthorizationCredentials = Depends(
        JWTBearer(scheme_name="Integration Token")
    ),
) -> IntegrationConnection:
    decoded_token = jwt.decode(
        jwt_creds.credentials, config.jwt_secret_key, algorithms=[config.jwt_algorithm]
    )
    integration_connection_id: str = decoded_token["integration_connection_id"]

    integration_connection = IntegrationConnection.get_by_id(
        db, integration_connection_id
    )

    if not integration_connection:
        raise HTTPException(status_code=403, detail="Invalid token.")

    integration_connection.last_used = datetime.utcnow()
    db.commit()
    return integration_connection
