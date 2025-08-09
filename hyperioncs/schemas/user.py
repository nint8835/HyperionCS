from pydantic import BaseModel


class SessionUser(BaseModel):
    id: str
