from fastapi import APIRouter, Depends

from ...dependencies import get_integration
from ...models.currencies import Currency
from ...models.integrations import Integration, IntegrationConnection
from ...schemas.currencies import CurrencySchema
from ...schemas.integrations import IntegrationConnectionSchema, IntegrationSchema

integration_router = APIRouter(tags=["Integrations"])


@integration_router.get("", response_model=IntegrationSchema, name="Get Integration")
def get_integration_route(
    integration: IntegrationConnection = Depends(get_integration),
) -> Integration:
    """Retrieve details on the integration the provided integration token is for."""
    return integration.integration


@integration_router.get("/connection", response_model=IntegrationConnectionSchema)
def get_integration_connection(
    integration: IntegrationConnection = Depends(get_integration),
) -> IntegrationConnection:
    """Retrieve details on the integration connection that owns the provided integration token."""
    return integration


@integration_router.get("/currency", response_model=CurrencySchema)
def get_integration_currency(
    integration: IntegrationConnection = Depends(get_integration),
) -> Currency:
    """Retrieve details on the currency this integration is connected to."""
    return integration.currency
