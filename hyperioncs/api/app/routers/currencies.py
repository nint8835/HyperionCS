from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from hyperioncs.api.app.schemas.currencies import (
    CreateCurrencySchema,
    CurrencyPermissionsSchema,
    EditCurrencySchema,
)
from hyperioncs.db.models.currency import Currency
from hyperioncs.db.models.currency_permission import (
    CurrencyActionRoles,
    CurrencyPermission,
    CurrencyRole,
)
from hyperioncs.db.models.integration import Integration
from hyperioncs.db.models.integration_connection import IntegrationConnection
from hyperioncs.dependencies.auth import get_session_user, require_session_user
from hyperioncs.dependencies.database import get_db
from hyperioncs.schemas import ErrorResponseSchema
from hyperioncs.schemas.currencies import CurrencySchema
from hyperioncs.schemas.integrations import IntegrationSchema
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
        },
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
        permission = CurrencyPermission(
            user_id=current_user.id,
            currency_shortcode=currency.shortcode,
            role=CurrencyRole.Owner,
        )
        db.add(new_currency)
        db.add(permission)

        await db.commit()

        return new_currency


@currencies_router.patch(
    "/{shortcode}",
    response_model=CurrencySchema,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "Unauthorized",
            "model": ErrorResponseSchema,
        }
    },
)
async def edit_currency(
    shortcode: str,
    currency: EditCurrencySchema,
    db: AsyncSession = Depends(get_db),
    current_user: SessionUser = Depends(require_session_user),
):
    """Edit an existing currency."""
    async with db.begin():
        existing_currency = (
            await db.execute(
                select(Currency)
                .filter_by(shortcode=shortcode)
                .join(
                    CurrencyPermission,
                    CurrencyPermission.currency_shortcode == Currency.shortcode,
                )
                .filter(CurrencyPermission.user_id == current_user.id)
                .filter(CurrencyPermission.role.in_(CurrencyActionRoles.Edit))
            )
        ).scalar_one_or_none()

        if not existing_currency:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content=ErrorResponseSchema(
                    detail="The requested currency doesn't exist or you do not have permission to edit it."
                ).model_dump(),
            )

        existing_currency.name = currency.name
        existing_currency.singular_form = currency.singular_form
        existing_currency.plural_form = currency.plural_form

        await db.commit()

        return existing_currency


@currencies_router.get(
    "/{shortcode}/permissions", response_model=CurrencyPermissionsSchema
)
async def get_currency_permissions(
    shortcode: str,
    db: AsyncSession = Depends(get_db),
    current_user: SessionUser = Depends(get_session_user),
):
    """Get the permissions the current user has on a given currency."""
    if not current_user:
        return CurrencyPermissionsSchema.from_role(None)

    permissions = (
        (
            await db.execute(
                select(CurrencyPermission).filter_by(
                    currency_shortcode=shortcode, user_id=current_user.id
                )
            )
        )
        .scalars()
        .one_or_none()
    )

    return CurrencyPermissionsSchema.from_role(
        permissions.role if permissions else None
    )


# TODO: Should this be optionally returned straight from the currency get API?
@currencies_router.get(
    "/{shortcode}/integrations",
    response_model=list[IntegrationSchema],
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "Unauthorized",
            "model": ErrorResponseSchema,
        }
    },
)
async def get_currency_integrations(
    shortcode: str,
    db: AsyncSession = Depends(get_db),
    current_user: SessionUser = Depends(get_session_user),
):
    """Get the integrations linked to a given currency."""
    # TODO: Should this permit anyone with edit permissions to see integrations?
    currency_permission = (
        await db.execute(
            select(CurrencyPermission)
            .filter_by(currency_shortcode=shortcode, user_id=current_user.id)
            .filter(CurrencyPermission.role.in_(CurrencyActionRoles.ConnectIntegration))
        )
    ).scalar_one_or_none()

    if currency_permission is None:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=ErrorResponseSchema(
                detail="The requested currency doesn't exist or you do not have permission to view its integrations."
            ).model_dump(),
        )

    return (
        (
            await db.execute(
                select(Integration).join(
                    IntegrationConnection,
                    and_(
                        IntegrationConnection.integration_id == Integration.id,
                        IntegrationConnection.currency_shortcode == shortcode,
                    ),
                )
            )
        )
        .scalars()
        .all()
    )
