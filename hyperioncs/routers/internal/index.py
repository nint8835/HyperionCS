from typing import Any, Dict

from fastapi import APIRouter, Depends, Request

from ...dependencies import get_discord_user, get_integration
from ...models.integrations import IntegrationConnection
from ...schemas import DiscordUser

index_router = APIRouter()


@index_router.get("/users/me", response_model=DiscordUser)
def current_user(
    request: Request, user: DiscordUser = Depends(get_discord_user)
) -> DiscordUser:
    return user


@index_router.get("/integration_test")
def integration_test(
    request: Request, integration: IntegrationConnection = Depends(get_integration)
) -> Dict[str, Any]:
    return {
        "id": integration.id,
        "currency_id": integration.currency_id,
        "integration_id": integration.integration_id,
    }
