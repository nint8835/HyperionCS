from fastapi import Depends, FastAPI
from fastapi.routing import APIRoute

from hyperioncs.api.integrations.v1.routers.currencies import currencies_router
from hyperioncs.dependencies.auth import require_integration
from hyperioncs.schemas.integrations import IntegrationSchema


def generate_unique_id(route: APIRoute) -> str:
    return route.name


integrations_api_v1 = FastAPI(
    title="Hyperion Integrations API",
    version="1.0",
    generate_unique_id_function=generate_unique_id,
)

integrations_api_v1.include_router(currencies_router, prefix="/currencies")


@integrations_api_v1.get("/whoami", response_model=IntegrationSchema)
async def whoami(
    integration: IntegrationSchema = Depends(require_integration),
) -> IntegrationSchema:
    """Get details about the currently authenticated integration."""
    return integration
