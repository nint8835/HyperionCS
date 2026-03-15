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


class IntegrationTokenSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(description="The unique identifier of the token.")
    name: str = Field(description="The name of the token.")


class CreatedIntegrationTokenSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(description="The unique identifier of the token.")
    name: str = Field(description="The name of the token.")
    token: str = Field(description="The JWT token value. Only returned at creation time.")
