from fastapi import APIRouter, Request
from pydantic import BaseModel

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
def index_route(request: Request) -> UserResponse:
    return UserResponse(**request.session["user"])
