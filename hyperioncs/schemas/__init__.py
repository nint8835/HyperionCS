from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field


class ErrorResponseSchema(BaseModel):
    """A generic error response."""

    detail: str = Field(description="A description of the error.")


# Custom type that converts empty strings to None
NullableString = Annotated[
    str | None, BeforeValidator(lambda v: None if v == "" else v)
]
