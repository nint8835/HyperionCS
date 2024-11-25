from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from .config import config
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
