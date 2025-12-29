import jwt
from authlib.integrations.starlette_client import OAuth
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from hyperioncs.config import config
from hyperioncs.db.models.integration import Integration
from hyperioncs.db.models.integration_token import IntegrationToken
from hyperioncs.dependencies.database import get_db
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
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be logged in to access this API.",
            headers={"Content-Type": "application/json"},
        )

    return user


class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        credentials = await super().__call__(request)

        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You must be authenticated to access this API.",
                headers={"Content-Type": "application/json"},
            )

        if credentials.scheme != "Bearer":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid authentication scheme.",
                headers={"Content-Type": "application/json"},
            )

        if not self.verify_jwt(credentials.credentials):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token.",
                headers={"Content-Type": "application/json"},
            )

        return credentials

    def verify_jwt(self, given_jwt: str) -> bool:
        try:
            decoded_token = jwt.decode(
                given_jwt, config.jwt_secret, algorithms=[config.jwt_algorithm]
            )

            if "token_id" not in decoded_token:
                return False

            return True
        except jwt.DecodeError:
            return False


async def require_integration(
    request: Request,
    db: AsyncSession = Depends(get_db),
    jwt_creds: HTTPAuthorizationCredentials = Depends(
        JWTBearer(scheme_name="Integration Token", bearerFormat="JWT")
    ),
) -> Integration:
    decoded_token = jwt.decode(
        jwt_creds.credentials, config.jwt_secret, algorithms=[config.jwt_algorithm]
    )
    token_id: str = decoded_token["token_id"]

    integration = (
        await db.execute(
            select(Integration).join(
                IntegrationToken,
                and_(
                    IntegrationToken.id == token_id,
                    IntegrationToken.integration_id == Integration.id,
                ),
            )
        )
    ).scalar_one_or_none()

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired integration token.",
            headers={"Content-Type": "application/json"},
        )

    return integration
