from typing import Optional

from pydantic import BaseModel


class DiscordUser(BaseModel):
    id: str
    username: str
    avatar: Optional[str] = None
    discriminator: str
    public_flags: int
    flags: int
    locale: str
    mfa_enabled: bool
    premium_type: int
    email: str
    verified: bool
