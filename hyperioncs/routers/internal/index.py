from fastapi import APIRouter, Depends

from hyperioncs.dependencies import get_discord_user
from hyperioncs.schemas import DiscordUser

index_router = APIRouter()


@index_router.get("/users/me", response_model=DiscordUser, include_in_schema=False)
def current_user(user: DiscordUser = Depends(get_discord_user)) -> DiscordUser:
    return user
