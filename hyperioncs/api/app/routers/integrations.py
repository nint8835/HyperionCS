from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import and_, not_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from hyperioncs.api.app.schemas.integrations import (
    ConnectIntegrationSchema,
    CreateIntegrationSchema,
)
from hyperioncs.db.models.currency import Currency
from hyperioncs.db.models.currency_permission import (
    CurrencyActionRoles,
    CurrencyPermission,
)
from hyperioncs.db.models.integration import Integration
from hyperioncs.db.models.integration_connection import IntegrationConnection
from hyperioncs.db.models.integration_permission import (
    IntegrationActionRoles,
    IntegrationPermission,
    IntegrationRole,
)
from hyperioncs.db.models.utils import default_uuid_str
from hyperioncs.dependencies.auth import require_session_user
from hyperioncs.dependencies.database import get_db
from hyperioncs.schemas import ErrorResponseSchema
from hyperioncs.schemas.integrations import IntegrationSchema
from hyperioncs.schemas.user import SessionUser

integrations_router = APIRouter(tags=["Integrations"])


@integrations_router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=IntegrationSchema
)
async def create_integration(
    integration: CreateIntegrationSchema,
    db: AsyncSession = Depends(get_db),
    current_user: SessionUser = Depends(require_session_user),
):
    """Create a new integration."""

    async with db.begin():
        new_integration = Integration(
            # Need to explicitly set so it can be referenced in the permission
            # https://docs.sqlalchemy.org/en/20/faq/ormconfiguration.html#defaults-default-factory-insert-default
            # Need to turn on mapping to dataclasses to make this unnecessary, but that takes greater work
            # https://docs.sqlalchemy.org/en/20/orm/dataclasses.html#orm-declarative-native-dataclasses
            id=default_uuid_str(),
            name=integration.name,
            description=integration.description,
            url=integration.url,
            private=True,
        )
        permission = IntegrationPermission(
            user_id=current_user.id,
            integration_id=new_integration.id,
            role=IntegrationRole.Owner,
        )
        db.add(new_integration)
        db.add(permission)

        await db.commit()

        return new_integration


@integrations_router.get("/", response_model=list[IntegrationSchema])
async def list_integrations(
    db: AsyncSession = Depends(get_db),
    current_user: SessionUser = Depends(require_session_user),
):
    """List all integrations the current user has access to."""
    return (
        (
            await db.execute(
                select(Integration)
                .join(
                    IntegrationPermission,
                    and_(
                        IntegrationPermission.user_id == current_user.id,
                        IntegrationPermission.integration_id == Integration.id,
                        IntegrationPermission.role.in_(IntegrationActionRoles.Connect),
                    ),
                    isouter=True,
                )
                .filter(
                    or_(not_(Integration.private), IntegrationPermission.id.isnot(None))
                )
            )
        )
        .scalars()
        .all()
    )


# TODO: Should this and the disconnect endpoint be made more restful?
# TODO: Can the permission logic between the two apis be deduplicated?
@integrations_router.post(
    "/{integration_id}/connect",
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "Unauthorized",
            "model": ErrorResponseSchema,
        },
        status.HTTP_409_CONFLICT: {
            "description": "Integration Already Connected",
            "model": ErrorResponseSchema,
        },
    },
)
async def connect_integration(
    integration_id: str,
    body: ConnectIntegrationSchema,
    db: AsyncSession = Depends(get_db),
    current_user: SessionUser = Depends(require_session_user),
):
    """Connect an integration to a currency."""
    async with db.begin():
        integration = (
            await db.execute(
                select(Integration)
                .filter_by(id=integration_id)
                .join(
                    IntegrationPermission,
                    and_(
                        IntegrationPermission.user_id == current_user.id,
                        IntegrationPermission.integration_id == Integration.id,
                        IntegrationPermission.role.in_(IntegrationActionRoles.Connect),
                    ),
                    isouter=True,
                )
                .filter(
                    or_(not_(Integration.private), IntegrationPermission.id.isnot(None))
                )
            )
        ).scalar_one_or_none()

        if not integration:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content=ErrorResponseSchema(
                    detail="The requested integration could not be found or you do not have permission to connect it."
                ).model_dump(),
            )

        currency = (
            await db.execute(
                select(Currency)
                .filter_by(shortcode=body.currency_shortcode)
                .join(
                    CurrencyPermission,
                    and_(
                        CurrencyPermission.user_id == current_user.id,
                        CurrencyPermission.currency_shortcode == Currency.shortcode,
                        CurrencyPermission.role.in_(
                            CurrencyActionRoles.ConnectIntegration
                        ),
                    ),
                )
            )
        ).scalar_one_or_none()

        if not currency:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content=ErrorResponseSchema(
                    detail="The requested currency could not be found or you do not have permission to connect an integration to it."
                ).model_dump(),
            )

        existing_connection = (
            await db.execute(
                select(IntegrationConnection).filter_by(
                    integration_id=integration.id, currency_shortcode=currency.shortcode
                )
            )
        ).scalar_one_or_none()

        if existing_connection:
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content=ErrorResponseSchema(
                    detail="The integration is already connected to the specified currency."
                ).model_dump(),
            )

        new_connection = IntegrationConnection(
            integration_id=integration.id,
            currency_shortcode=currency.shortcode,
        )
        db.add(new_connection)

        await db.commit()

    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content={})


@integrations_router.post(
    "/{integration_id}/disconnect",
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "Unauthorized",
            "model": ErrorResponseSchema,
        },
        status.HTTP_409_CONFLICT: {
            "description": "Integration Not Connected",
            "model": ErrorResponseSchema,
        },
    },
)
async def disconnect_integration(
    integration_id: str,
    body: ConnectIntegrationSchema,
    db: AsyncSession = Depends(get_db),
    current_user: SessionUser = Depends(require_session_user),
):
    """Disconnect an integration from a currency."""
    async with db.begin():
        integration = (
            await db.execute(
                select(Integration)
                .filter_by(id=integration_id)
                .join(
                    IntegrationPermission,
                    and_(
                        IntegrationPermission.user_id == current_user.id,
                        IntegrationPermission.integration_id == Integration.id,
                        IntegrationPermission.role.in_(IntegrationActionRoles.Connect),
                    ),
                    isouter=True,
                )
                .filter(
                    or_(not_(Integration.private), IntegrationPermission.id.isnot(None))
                )
            )
        ).scalar_one_or_none()

        if not integration:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content=ErrorResponseSchema(
                    detail="The requested integration could not be found or you do not have permission to disconnect it."
                ).model_dump(),
            )

        currency = (
            await db.execute(
                select(Currency)
                .filter_by(shortcode=body.currency_shortcode)
                .join(
                    CurrencyPermission,
                    and_(
                        CurrencyPermission.user_id == current_user.id,
                        CurrencyPermission.currency_shortcode == Currency.shortcode,
                        CurrencyPermission.role.in_(
                            CurrencyActionRoles.ConnectIntegration
                        ),
                    ),
                )
            )
        ).scalar_one_or_none()

        if not currency:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content=ErrorResponseSchema(
                    detail="The requested currency could not be found or you do not have permission to disconnect an integration from it."
                ).model_dump(),
            )

        existing_connection = (
            await db.execute(
                select(IntegrationConnection).filter_by(
                    integration_id=integration.id, currency_shortcode=currency.shortcode
                )
            )
        ).scalar_one_or_none()

        if not existing_connection:
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content=ErrorResponseSchema(
                    detail="The integration is not connected to the specified currency."
                ).model_dump(),
            )

        await db.delete(existing_connection)

        await db.commit()

    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content={})
