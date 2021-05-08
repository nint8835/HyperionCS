from typing import Any, Dict

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from ..dependencies import get_current_user, get_integration
from ..models.integrations import IntegrationConnection

index_router = APIRouter()


class UserResponse(BaseModel):
    id: str
    username: str
    avatar: str
    discriminator: str
    public_flags: int
    flags: int
    locale: str
    mfa_enabled: bool
    premium_type: int
    email: str
    verified: bool


@index_router.get("/users/me", response_model=UserResponse)
def current_user(
    request: Request, user: Dict[Any, Any] = Depends(get_current_user)
) -> UserResponse:
    return UserResponse(**user)


@index_router.get("/integration_test")
def integration_test(
    request: Request, integration: IntegrationConnection = Depends(get_integration)
) -> Dict[str, Any]:
    return {
        "id": integration.id,
        "currency_id": integration.currency_id,
        "integration_id": integration.integration_id,
    }
