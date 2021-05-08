from fastapi import APIRouter, Depends

from ...dependencies import get_discord_user
from ...schemas import DiscordUser

index_router = APIRouter()


@index_router.get("/users/me", response_model=DiscordUser)
def current_user(user: DiscordUser = Depends(get_discord_user)) -> DiscordUser:
    return user
