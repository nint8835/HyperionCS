from fastapi import APIRouter, Depends, Request

from ...dependencies import get_integration
from ...models.integrations import Integration, IntegrationConnection
from ...schemas.integrations import IntegrationConnectionSchema, IntegrationSchema

integration_router = APIRouter()


@integration_router.get("/", response_model=IntegrationSchema, name="Get Integration")
def get_integration_route(
    request: Request, integration: IntegrationConnection = Depends(get_integration)
) -> Integration:
    return integration.integration


@integration_router.get("/connection", response_model=IntegrationConnectionSchema)
def get_integration_connection(
    request: Request, integration: IntegrationConnection = Depends(get_integration)
) -> IntegrationConnection:
    return integration
