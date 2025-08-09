from pydantic import BaseModel, ConfigDict, Field


class CreateCurrencySchema(BaseModel):
    shortcode: str = Field(
        description="A unique shortcode to identify the currency.",
        pattern=r"^[A-Z0-9]{3,5}$",
    )
    name: str = Field(description="The full name of the currency.")
    singular_form: str = Field(description="The singular form of the currency.")
    plural_form: str = Field(description="The plural form of the currency.")


class CurrencySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    shortcode: str = Field(description="The unique shortcode of the currency.")
    name: str = Field(description="The full name of the currency.")
    singular_form: str = Field(description="The singular form of the currency.")
    plural_form: str = Field(description="The plural form of the currency.")
