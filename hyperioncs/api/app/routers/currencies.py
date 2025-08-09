from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hyperioncs.api.app.schemas import ErrorResponseSchema
from hyperioncs.api.app.schemas.currencies import CreateCurrencySchema
from hyperioncs.db.models.currency import Currency
from hyperioncs.db.models.permission import Permission, PermissionRole
from hyperioncs.dependencies.auth import require_session_user
from hyperioncs.dependencies.database import get_db
from hyperioncs.schemas.currencies import CurrencySchema
from hyperioncs.schemas.user import SessionUser

currencies_router = APIRouter(tags=["Currencies"])


@currencies_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=CurrencySchema,
    responses={
        status.HTTP_409_CONFLICT: {
            "description": "Conflicting Shortcode",
            "model": ErrorResponseSchema,
        }
    },
)
async def create_currency(
    currency: CreateCurrencySchema,
    db: AsyncSession = Depends(get_db),
    current_user: SessionUser = Depends(require_session_user),
):
    """Create a new currency."""

    async with db.begin():
        existing_currency = (
            await db.execute(select(Currency).filter_by(shortcode=currency.shortcode))
        ).scalar_one_or_none()
        if existing_currency:
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content=ErrorResponseSchema(
                    detail="Currency with this shortcode already exists."
                ).model_dump(),
            )

        new_currency = Currency(
            shortcode=currency.shortcode,
            name=currency.name,
            singular_form=currency.singular_form,
            plural_form=currency.plural_form,
        )
        permission = Permission(
            user_id=current_user.id,
            currency_shortcode=currency.shortcode,
            role=PermissionRole.Owner,
        )
        db.add(new_currency)
        db.add(permission)

        await db.commit()

        return new_currency
