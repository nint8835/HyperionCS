from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hyperioncs.db.models.currency import Currency
from hyperioncs.dependencies.database import get_db
from hyperioncs.schemas import ErrorResponseSchema
from hyperioncs.schemas.currencies import CurrencySchema

currencies_router = APIRouter(tags=["Currencies"])


@currencies_router.get("/", response_model=list[CurrencySchema])
async def list_currencies(db: AsyncSession = Depends(get_db)):
    """List all currencies."""

    return (await db.execute(select(Currency))).scalars().all()


@currencies_router.get(
    "/{shortcode}",
    response_model=CurrencySchema,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Currency Not Found",
            "model": ErrorResponseSchema,
        }
    },
)
async def get_currency(shortcode: str, db: AsyncSession = Depends(get_db)):
    """Get a currency by its shortcode."""

    currency = (
        await db.execute(select(Currency).filter_by(shortcode=shortcode))
    ).scalar_one_or_none()
    if not currency:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponseSchema(
                detail="The requested currency doesn't exist."
            ).model_dump(),
        )

    return currency
