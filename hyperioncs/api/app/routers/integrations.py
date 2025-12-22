from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from hyperioncs.api.app.schemas.integrations import CreateIntegrationSchema
from hyperioncs.db.models.integration import Integration
from hyperioncs.db.models.integration_permission import (
    IntegrationPermission,
    IntegrationRole,
)
from hyperioncs.db.models.utils import default_uuid_str
from hyperioncs.dependencies.auth import require_session_user
from hyperioncs.dependencies.database import get_db
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
