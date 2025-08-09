from fastapi import FastAPI
from fastapi.routing import APIRoute

from hyperioncs.api.integrations.v1.routers.currencies import currencies_router


def generate_unique_id(route: APIRoute) -> str:
    return route.name


integrations_api_v1 = FastAPI(
    title="Hyperion Integrations API",
    version="1.0",
    generate_unique_id_function=generate_unique_id,
)

integrations_api_v1.include_router(currencies_router, prefix="/currencies")
