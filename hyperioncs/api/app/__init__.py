from typing import TypedDict

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from hyperioncs.config import config
from hyperioncs.db.models.testing import TestModel
from hyperioncs.dependencies.database import get_db


# Needed to prevent type issues applying kwargs to FastAPI. Really with Python's type system could handle this.
class FastAPIKwargs(TypedDict, total=False):
    docs_url: str | None
    redoc_url: str | None
    openapi_url: str | None


app_kwargs: FastAPIKwargs = (
    {"docs_url": None, "redoc_url": None, "openapi_url": None}
    if config.is_production
    else {}
)
main_app = FastAPI(title="Hyperion Web App", **app_kwargs)


@main_app.get("/db-test")
async def db_test(db: AsyncSession = Depends(get_db)) -> int:
    """Test endpoint to verify database connection."""
    async with db.begin():
        new_test = TestModel(name="Test Entry")
        db.add(new_test)
        await db.commit()

    return new_test.id
