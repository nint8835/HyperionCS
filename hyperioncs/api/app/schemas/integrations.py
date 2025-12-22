from pydantic import BaseModel, Field

from hyperioncs.schemas import NullableString


class CreateIntegrationSchema(BaseModel):
    name: str = Field(description="The name of the integration.")
    description: str = Field(description="A description of the integration.")
    url: NullableString = Field(
        default=None, description="URL to the website for the integration."
    )
