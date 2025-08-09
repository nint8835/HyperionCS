from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hyperioncs.db.models.currency import Currency
from hyperioncs.dependencies.database import get_db
from hyperioncs.schemas.currencies import CurrencySchema

currencies_router = APIRouter(tags=["Currencies"])


@currencies_router.get("/", response_model=list[CurrencySchema])
async def list_currencies(db: AsyncSession = Depends(get_db)):
    """List all currencies."""

    return (await db.execute(select(Currency))).scalars().all()
