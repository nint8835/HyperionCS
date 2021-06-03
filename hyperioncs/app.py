from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from .config import config
from .database import engine
from .routers.integrations import (
    accounts_router,
    integration_router,
    transaction_router,
)
from .routers.internal import auth_router, index_router

app = FastAPI(title="Hyperion Currency System")
app.add_middleware(SessionMiddleware, secret_key=config.secret_key)

app.include_router(auth_router)
app.include_router(index_router)

app.include_router(integration_router, prefix="/api/v1/integration")
app.include_router(accounts_router, prefix="/api/v1/accounts")
app.include_router(transaction_router, prefix="/api/v1/transactions")

if config.use_honeycomb:
    # WIP: This absolutely _tanks_ the request times - figure out why it does so.
    from grpc import ssl_channel_credentials
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor

    provider = TracerProvider(
        resource=Resource(attributes={"service.name": "hyperioncs"})
    )
    trace.set_tracer_provider(provider)

    otlp_exporter = OTLPSpanExporter(
        endpoint="api.honeycomb.io:443",
        insecure=False,
        credentials=ssl_channel_credentials(),
        headers=(
            ("x-honeycomb-team", config.honeycomb_api_key),
            ("x-honeycomb-dataset", config.honeycomb_dataset),
        ),
    )
    provider.add_span_processor(SimpleSpanProcessor(otlp_exporter))

    FastAPIInstrumentor.instrument_app(app)
    SQLAlchemyInstrumentor().instrument(engine=engine)


app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")
templates = Jinja2Templates(directory="frontend/build")


@app.get("/{rest_of_path:path}", include_in_schema=False)
async def serve_frontend(request: Request, rest_of_path: str) -> Response:
    return templates.TemplateResponse("index.html", {"request": request})
