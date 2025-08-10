from pydantic import BaseModel, Field


class CreateCurrencySchema(BaseModel):
    shortcode: str = Field(
        description="A unique shortcode to identify the currency.",
        pattern=r"^[A-Z0-9]{3,5}$",
    )
    name: str = Field(description="The full name of the currency.")
    singular_form: str = Field(description="The singular form of the currency.")
    plural_form: str = Field(description="The plural form of the currency.")


class EditCurrencySchema(BaseModel):
    name: str = Field(description="The full name of the currency.")
    singular_form: str = Field(description="The singular form of the currency.")
    plural_form: str = Field(description="The plural form of the currency.")
