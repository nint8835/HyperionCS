from pydantic import BaseModel, Field


class SessionUser(BaseModel):
    """Details of the currently authenticated user."""

    id: str = Field(description="Discord snowflake of the authenticated user.")
