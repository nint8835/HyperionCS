from pydantic import BaseModel, ConfigDict, Field


class IntegrationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(description="The unique identifier of the integration.")
    name: str = Field(description="The name of the integration.")
    description: str = Field(description="A description of the integration.")
    url: str | None = Field(
        default=None, description="URL to the website for the integration."
    )
    private: bool = Field(description="Whether the integration is private.")
