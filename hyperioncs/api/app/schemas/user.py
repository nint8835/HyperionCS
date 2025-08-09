from pydantic import BaseModel


class DiscordUser(BaseModel):
    id: str
