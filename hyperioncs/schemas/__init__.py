from pydantic import BaseModel, Field


class ErrorResponseSchema(BaseModel):
    """A generic error response."""

    detail: str = Field(description="A description of the error.")
