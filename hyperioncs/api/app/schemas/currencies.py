from typing import Self

from pydantic import BaseModel, Field

from hyperioncs.db.models.currency_permission import CurrencyActionRoles, CurrencyRole


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


# TODO: See if there's a smarter way to do this
class CurrencyPermissionsSchema(BaseModel):
    edit: bool = Field(
        description="Whether the user can edit the currency.", default=False
    )

    @classmethod
    def from_role(cls, role: CurrencyRole | None) -> Self:
        if role is None:
            return cls()

        return cls(
            edit=role in CurrencyActionRoles.Edit,
        )
