from starlette.applications import Starlette
from starlette.routing import Mount

from hyperioncs.api.app import main_app
from hyperioncs.api.integrations.v1 import integrations_api_v1

app = Starlette(
    routes=[
        Mount("/api/v1", integrations_api_v1),
        Mount("/", main_app),
    ],
)
