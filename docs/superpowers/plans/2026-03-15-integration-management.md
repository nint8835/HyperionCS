# Integration Management Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add comprehensive integration management — a list page, a management page with metadata editing and token management, and a new View role — to HyperionCS.

**Architecture:** Backend-first: amend the data model and add new FastAPI endpoints, then regenerate the frontend query client, then build the frontend pages. All backend endpoints live in the existing `integrations_router`. The frontend follows the established patterns from the currencies pages.

**Tech Stack:** Python/FastAPI/SQLAlchemy/Alembic (backend), React/TanStack Router/TanStack Query/HeroUI/@tanstack/react-form (frontend), `@openapi-codegen` for client generation.

**Spec:** `docs/superpowers/specs/2026-03-15-integration-management-design.md`

---

## File Map

**Backend — modified:**
- `hyperioncs/db/models/integration_permission.py` — add `View` role and `IntegrationActionRoles.View`
- `hyperioncs/db/models/integration_token.py` — add `name: Mapped[str]` field
- `hyperioncs/migrations/versions/781cb27e06c3_create_integration_token_model.py` — amend to include `name` column
- `hyperioncs/schemas/integrations.py` — add `IntegrationTokenSchema`, `CreatedIntegrationTokenSchema`
- `hyperioncs/api/app/schemas/integrations.py` — add `EditIntegrationSchema`, `CreateIntegrationTokenSchema`
- `hyperioncs/api/app/routers/integrations.py` — add 6 new endpoints, extend list endpoint

**Frontend — modified:**
- `frontend/src/routes/__root.tsx` — add Integrations navbar link

**Frontend — created:**
- `frontend/src/routes/integrations/index.tsx` — integrations list page
- `frontend/src/routes/integrations/$integrationId/manage.tsx` — integration management page

**Frontend — modified:**
- `frontend/src/routes/integrations/create.tsx` — redirect to list after creation

---

## Chunk 1: Backend — Data Model & Schemas

### Task 1: Add `View` role to `IntegrationRole`

**Files:**
- Modify: `hyperioncs/db/models/integration_permission.py`

- [ ] **Open `hyperioncs/db/models/integration_permission.py` and add the `View` role.**

  Replace the file with:

  ```python
  import enum
  from typing import TYPE_CHECKING

  from sqlalchemy import ForeignKey
  from sqlalchemy.orm import Mapped, mapped_column, relationship

  from hyperioncs.db import Base
  from hyperioncs.db.models.utils import default_uuid_str

  if TYPE_CHECKING:
      from .integration import Integration


  class IntegrationRole(enum.Enum):
      Owner = "owner"
      View = "view"


  class IntegrationActionRoles:
      Edit = [IntegrationRole.Owner]
      Connect = [IntegrationRole.Owner]
      View = [IntegrationRole.View, IntegrationRole.Owner]


  class IntegrationPermission(Base):
      __tablename__ = "integration_permissions"

      id: Mapped[str] = mapped_column(primary_key=True, default=default_uuid_str)
      user_id: Mapped[str]
      integration_id: Mapped[str] = mapped_column(
          ForeignKey("integrations.id", ondelete="CASCADE")
      )
      integration: Mapped["Integration"] = relationship(lazy="raise")

      role: Mapped[IntegrationRole]
  ```

- [ ] **Verify the import still works:**

  ```bash
  uv run python -c "from hyperioncs.db.models.integration_permission import IntegrationRole, IntegrationActionRoles; print(IntegrationActionRoles.View)"
  ```

  Expected: `[<IntegrationRole.View: 'view'>, <IntegrationRole.Owner: 'owner'>]`

- [ ] **Commit:**

  ```bash
  git add hyperioncs/db/models/integration_permission.py
  git commit -m "feat: add View role to IntegrationRole"
  ```

---

### Task 2: Add `name` to `IntegrationToken` model and amend migration

**Files:**
- Modify: `hyperioncs/db/models/integration_token.py`
- Modify: `hyperioncs/migrations/versions/781cb27e06c3_create_integration_token_model.py`

- [ ] **Update `hyperioncs/db/models/integration_token.py` to add `name`:**

  ```python
  from typing import TYPE_CHECKING

  from sqlalchemy import ForeignKey
  from sqlalchemy.orm import Mapped, mapped_column, relationship

  from hyperioncs.db import Base
  from hyperioncs.db.models.utils import default_uuid_str

  if TYPE_CHECKING:
      from .integration import Integration


  class IntegrationToken(Base):
      __tablename__ = "integration_tokens"

      id: Mapped[str] = mapped_column(primary_key=True, default=default_uuid_str)
      integration_id: Mapped[str] = mapped_column(
          ForeignKey("integrations.id", ondelete="CASCADE")
      )
      name: Mapped[str]

      integration: Mapped["Integration"] = relationship(lazy="raise")
  ```

- [ ] **Amend `hyperioncs/migrations/versions/781cb27e06c3_create_integration_token_model.py` to include the `name` column:**

  ```python
  """Create integration token model

  Revision ID: 781cb27e06c3
  Revises: 97118cf7629a
  Create Date: 2025-12-29 18:03:43.785881

  """

  from typing import Sequence, Union

  import sqlalchemy as sa
  from alembic import op

  # revision identifiers, used by Alembic.
  revision: str = "781cb27e06c3"
  down_revision: Union[str, Sequence[str], None] = "97118cf7629a"
  branch_labels: Union[str, Sequence[str], None] = None
  depends_on: Union[str, Sequence[str], None] = None


  def upgrade() -> None:
      op.create_table(
          "integration_tokens",
          sa.Column("id", sa.String(), nullable=False),
          sa.Column("integration_id", sa.String(), nullable=False),
          sa.Column("name", sa.String(), nullable=False),
          sa.ForeignKeyConstraint(
              ["integration_id"],
              ["integrations.id"],
              name=op.f("fk_integration_tokens_integration_id_integrations"),
              ondelete="CASCADE",
          ),
          sa.PrimaryKeyConstraint("id", name=op.f("pk_integration_tokens")),
      )


  def downgrade() -> None:
      op.drop_table("integration_tokens")
  ```

- [ ] **Delete the existing database and re-run migrations** (no production data):

  ```bash
  rm -f hyperion.sqlite
  uv run python -m hyperioncs upgrade
  ```

  Expected: migration runs without error.

- [ ] **Commit:**

  ```bash
  git add hyperioncs/db/models/integration_token.py hyperioncs/migrations/versions/781cb27e06c3_create_integration_token_model.py
  git commit -m "feat: add name to IntegrationToken model"
  ```

---

### Task 3: Add new Pydantic schemas

**Files:**
- Modify: `hyperioncs/schemas/integrations.py`
- Modify: `hyperioncs/api/app/schemas/integrations.py`

- [ ] **Add `IntegrationTokenSchema` and `CreatedIntegrationTokenSchema` to `hyperioncs/schemas/integrations.py`:**

  ```python
  from pydantic import BaseModel, ConfigDict, Field


  class IntegrationSchema(BaseModel):
      model_config = ConfigDict(from_attributes=True)

      id: str = Field(description="The unique identifier of the integration.")
      name: str = Field(description="The name of the integration.")
      description: str = Field(description="A description of the integration.")
      url: str | None = Field(
          default=None, description="URL to the website for the integration."
      )
      private: bool = Field(description="Whether the integration is private.")


  class IntegrationTokenSchema(BaseModel):
      model_config = ConfigDict(from_attributes=True)

      id: str = Field(description="The unique identifier of the token.")
      name: str = Field(description="The name of the token.")


  class CreatedIntegrationTokenSchema(BaseModel):
      model_config = ConfigDict(from_attributes=True)

      id: str = Field(description="The unique identifier of the token.")
      name: str = Field(description="The name of the token.")
      token: str = Field(description="The JWT token value. Only returned at creation time.")
  ```

- [ ] **Add `EditIntegrationSchema` and `CreateIntegrationTokenSchema` to `hyperioncs/api/app/schemas/integrations.py`:**

  ```python
  from pydantic import BaseModel, Field

  from hyperioncs.schemas import NullableString


  class CreateIntegrationSchema(BaseModel):
      name: str = Field(description="The name of the integration.")
      description: str = Field(description="A description of the integration.")
      url: NullableString = Field(
          default=None, description="URL to the website for the integration."
      )


  class ConnectIntegrationSchema(BaseModel):
      currency_shortcode: str = Field(
          description="The shortcode of the currency to connect the integration to."
      )


  class EditIntegrationSchema(BaseModel):
      name: str = Field(description="The name of the integration.")
      description: str = Field(description="A description of the integration.")
      url: NullableString = Field(description="URL to the website for the integration.")


  class CreateIntegrationTokenSchema(BaseModel):
      name: str = Field(description="The name of the token.")
  ```

  Note: `EditIntegrationSchema.url` has **no default** — all three fields are required.

- [ ] **Verify imports work:**

  ```bash
  uv run python -c "from hyperioncs.api.app.schemas.integrations import EditIntegrationSchema, CreateIntegrationTokenSchema; from hyperioncs.schemas.integrations import IntegrationTokenSchema, CreatedIntegrationTokenSchema; print('ok')"
  ```

  Expected: `ok`

- [ ] **Commit:**

  ```bash
  git add hyperioncs/schemas/integrations.py hyperioncs/api/app/schemas/integrations.py
  git commit -m "feat: add integration token and edit schemas"
  ```

---

## Chunk 2: Backend — API Endpoints

### Task 4: Extend `list_integrations` with `manageable` param

**Files:**
- Modify: `hyperioncs/api/app/routers/integrations.py`

- [ ] **Update the `list_integrations` function signature and body.** Add `manageable: bool = False` as a `Query` param. When `True`, inner-join on Edit role instead of the existing outer-join/public logic.

  Replace the existing `list_integrations` function with:

  ```python
  @integrations_router.get("/", response_model=list[IntegrationSchema])
  async def list_integrations(
      manageable: bool = Query(False),
      db: AsyncSession = Depends(get_db),
      current_user: SessionUser = Depends(require_session_user),
  ):
      """List integrations visible to the current user.

      When manageable=true, returns only integrations the user can edit.
      Otherwise returns public integrations and integrations the user can connect.
      """
      if manageable:
          return (
              (
                  await db.execute(
                      select(Integration).join(
                          IntegrationPermission,
                          and_(
                              IntegrationPermission.user_id == current_user.id,
                              IntegrationPermission.integration_id == Integration.id,
                              IntegrationPermission.role.in_(IntegrationActionRoles.Edit),
                          ),
                      )
                  )
              )
              .scalars()
              .all()
          )

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
  ```

  Also add `Query` to the FastAPI imports at the top of the file:

  ```python
  from fastapi import APIRouter, Depends, Query, status
  ```

- [ ] **Verify the server starts and the endpoint appears in OpenAPI docs:**

  ```bash
  uv run python -m hyperioncs start
  ```

  Navigate to `http://localhost:8000/docs` and confirm `GET /api/internal/integrations/` now shows a `manageable` query param.

- [ ] **Commit:**

  ```bash
  git add hyperioncs/api/app/routers/integrations.py
  git commit -m "feat: add manageable filter to list integrations endpoint"
  ```

---

### Task 5: Add `get_integration` endpoint

> **Depends on Task 1** — `IntegrationActionRoles.View` must exist before this endpoint will work.

**Files:**
- Modify: `hyperioncs/api/app/routers/integrations.py`

- [ ] **Add the `get_integration` function after the `list_integrations` function.** No import changes are needed — `IntegrationActionRoles`, `IntegrationPermission`, and `IntegrationRole` are already imported.

  Add the endpoint after `list_integrations`:

  ```python
  @integrations_router.get(
      "/{integration_id}",
      response_model=IntegrationSchema,
      responses={
          status.HTTP_403_FORBIDDEN: {
              "description": "Unauthorized",
              "model": ErrorResponseSchema,
          }
      },
  )
  async def get_integration(
      integration_id: str,
      db: AsyncSession = Depends(get_db),
      current_user: SessionUser = Depends(require_session_user),
  ):
      """Get a single integration visible to the current user.

      Public integrations are accessible to all authenticated users.
      Private integrations require the View role.
      """
      integration = (
          await db.execute(
              select(Integration)
              .filter_by(id=integration_id)
              .join(
                  IntegrationPermission,
                  and_(
                      IntegrationPermission.user_id == current_user.id,
                      IntegrationPermission.integration_id == Integration.id,
                      IntegrationPermission.role.in_(IntegrationActionRoles.View),
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
                  detail="The requested integration could not be found or you do not have permission to view it."
              ).model_dump(),
          )

      return integration
  ```

- [ ] **Verify the endpoint appears in OpenAPI docs at `GET /api/internal/integrations/{integration_id}`.**

- [ ] **Commit:**

  ```bash
  git add hyperioncs/api/app/routers/integrations.py
  git commit -m "feat: add get_integration endpoint"
  ```

---

### Task 6: Add `edit_integration` endpoint

**Files:**
- Modify: `hyperioncs/api/app/routers/integrations.py`

- [ ] **Add the required import for `EditIntegrationSchema`** to the imports at the top of `integrations.py`:

  ```python
  from hyperioncs.api.app.schemas.integrations import (
      ConnectIntegrationSchema,
      CreateIntegrationSchema,
      EditIntegrationSchema,
  )
  ```

- [ ] **Add the `edit_integration` function after `get_integration`:**

  ```python
  @integrations_router.patch(
      "/{integration_id}",
      response_model=IntegrationSchema,
      responses={
          status.HTTP_403_FORBIDDEN: {
              "description": "Unauthorized",
              "model": ErrorResponseSchema,
          }
      },
  )
  async def edit_integration(
      integration_id: str,
      body: EditIntegrationSchema,
      db: AsyncSession = Depends(get_db),
      current_user: SessionUser = Depends(require_session_user),
  ):
      """Edit an integration's metadata. Requires Edit role."""
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
                          IntegrationPermission.role.in_(IntegrationActionRoles.Edit),
                      ),
                  )
              )
          ).scalar_one_or_none()

          if not integration:
              return JSONResponse(
                  status_code=status.HTTP_403_FORBIDDEN,
                  content=ErrorResponseSchema(
                      detail="The requested integration could not be found or you do not have permission to edit it."
                  ).model_dump(),
              )

          integration.name = body.name
          integration.description = body.description
          integration.url = body.url

          await db.commit()

          return integration
  ```

- [ ] **Verify endpoint appears in OpenAPI docs at `PATCH /api/internal/integrations/{integration_id}`.**

- [ ] **Commit:**

  ```bash
  git add hyperioncs/api/app/routers/integrations.py
  git commit -m "feat: add edit_integration endpoint"
  ```

---

### Task 7: Add token endpoints

> **Depends on Tasks 1 and 2** — `IntegrationActionRoles.Edit` must exist and `IntegrationToken.name` must be in the model/migration.

**Files:**
- Modify: `hyperioncs/api/app/routers/integrations.py`

- [ ] **Add the required imports** to the top of `integrations.py`. Make these changes to the existing import block — do not add duplicate import statements:

  1. Add `import jwt` near the top (with other stdlib/third-party imports).
  2. Add `from hyperioncs.config import config`.
  3. Add `from hyperioncs.db.models.integration_token import IntegrationToken`.
  4. Expand the existing `from hyperioncs.api.app.schemas.integrations import (...)` to include `CreateIntegrationTokenSchema` (it should already have `ConnectIntegrationSchema`, `CreateIntegrationSchema`, and after Task 6 `EditIntegrationSchema`).
  5. Expand the existing `from hyperioncs.schemas.integrations import IntegrationSchema` to also import `CreatedIntegrationTokenSchema` and `IntegrationTokenSchema`:

  ```python
  from hyperioncs.schemas.integrations import (
      CreatedIntegrationTokenSchema,
      IntegrationSchema,
      IntegrationTokenSchema,
  )
  ```

  The final imports block at the top of the file should contain exactly one import per module — no duplicates.

- [ ] **Add `list_integration_tokens` after the `edit_integration` function:**

  ```python
  @integrations_router.get(
      "/{integration_id}/tokens",
      response_model=list[IntegrationTokenSchema],
      responses={
          status.HTTP_403_FORBIDDEN: {
              "description": "Unauthorized",
              "model": ErrorResponseSchema,
          }
      },
  )
  async def list_integration_tokens(
      integration_id: str,
      db: AsyncSession = Depends(get_db),
      current_user: SessionUser = Depends(require_session_user),
  ):
      """List tokens for an integration. Requires Edit role."""
      integration = (
          await db.execute(
              select(Integration)
              .filter_by(id=integration_id)
              .join(
                  IntegrationPermission,
                  and_(
                      IntegrationPermission.user_id == current_user.id,
                      IntegrationPermission.integration_id == Integration.id,
                      IntegrationPermission.role.in_(IntegrationActionRoles.Edit),
                  ),
              )
          )
      ).scalar_one_or_none()

      if not integration:
          return JSONResponse(
              status_code=status.HTTP_403_FORBIDDEN,
              content=ErrorResponseSchema(
                  detail="The requested integration could not be found or you do not have permission to manage its tokens."
              ).model_dump(),
          )

      return (
          (
              await db.execute(
                  select(IntegrationToken).filter_by(integration_id=integration.id)
              )
          )
          .scalars()
          .all()
      )
  ```

- [ ] **Add `create_integration_token` after `list_integration_tokens`:**

  ```python
  @integrations_router.post(
      "/{integration_id}/tokens",
      status_code=status.HTTP_201_CREATED,
      response_model=CreatedIntegrationTokenSchema,
      responses={
          status.HTTP_403_FORBIDDEN: {
              "description": "Unauthorized",
              "model": ErrorResponseSchema,
          }
      },
  )
  async def create_integration_token(
      integration_id: str,
      body: CreateIntegrationTokenSchema,
      db: AsyncSession = Depends(get_db),
      current_user: SessionUser = Depends(require_session_user),
  ):
      """Create a new token for an integration. Requires Edit role.

      The token value is only returned in this response — it cannot be retrieved later.
      """
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
                          IntegrationPermission.role.in_(IntegrationActionRoles.Edit),
                      ),
                  )
              )
          ).scalar_one_or_none()

          if not integration:
              return JSONResponse(
                  status_code=status.HTTP_403_FORBIDDEN,
                  content=ErrorResponseSchema(
                      detail="The requested integration could not be found or you do not have permission to manage its tokens."
                  ).model_dump(),
              )

          token_id = default_uuid_str()
          new_token = IntegrationToken(
              id=token_id,
              integration_id=integration.id,
              name=body.name,
          )
          db.add(new_token)
          await db.commit()

      token_value = jwt.encode(
          {"token_id": token_id},
          config.jwt_secret,
          algorithm=config.jwt_algorithm,
      )

      return CreatedIntegrationTokenSchema(
          id=token_id,
          name=body.name,
          token=token_value,
      )
  ```

- [ ] **Add `delete_integration_token` after `create_integration_token`:**

  ```python
  @integrations_router.delete(
      "/{integration_id}/tokens/{token_id}",
      status_code=status.HTTP_202_ACCEPTED,
      responses={
          status.HTTP_403_FORBIDDEN: {
              "description": "Unauthorized",
              "model": ErrorResponseSchema,
          },
          status.HTTP_404_NOT_FOUND: {
              "description": "Token Not Found",
              "model": ErrorResponseSchema,
          },
      },
  )
  async def delete_integration_token(
      integration_id: str,
      token_id: str,
      db: AsyncSession = Depends(get_db),
      current_user: SessionUser = Depends(require_session_user),
  ):
      """Delete an integration token. Requires Edit role."""
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
                          IntegrationPermission.role.in_(IntegrationActionRoles.Edit),
                      ),
                  )
              )
          ).scalar_one_or_none()

          if not integration:
              return JSONResponse(
                  status_code=status.HTTP_403_FORBIDDEN,
                  content=ErrorResponseSchema(
                      detail="The requested integration could not be found or you do not have permission to manage its tokens."
                  ).model_dump(),
              )

          token = (
              await db.execute(
                  select(IntegrationToken).filter_by(
                      id=token_id, integration_id=integration.id
                  )
              )
          ).scalar_one_or_none()

          if not token:
              return JSONResponse(
                  status_code=status.HTTP_404_NOT_FOUND,
                  content=ErrorResponseSchema(
                      detail="The requested token could not be found."
                  ).model_dump(),
              )

          await db.delete(token)
          await db.commit()

      return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content={})
  ```

- [ ] **Verify the server starts cleanly:**

  ```bash
  uv run python -m hyperioncs start
  ```

  Check `http://localhost:8000/docs` — confirm all 6 new endpoints appear under `Integrations`:
  - `GET /api/internal/integrations/` (with `manageable` param)
  - `GET /api/internal/integrations/{integration_id}`
  - `PATCH /api/internal/integrations/{integration_id}`
  - `GET /api/internal/integrations/{integration_id}/tokens`
  - `POST /api/internal/integrations/{integration_id}/tokens`
  - `DELETE /api/internal/integrations/{integration_id}/tokens/{token_id}`

- [ ] **Commit:**

  ```bash
  git add hyperioncs/api/app/routers/integrations.py
  git commit -m "feat: add token management endpoints"
  ```

---

## Chunk 3: Frontend

### Task 8: Regenerate the frontend query client

**Files:**
- Regenerated: `frontend/src/queries/internal/internalComponents.ts` (and other files in that directory)

- [ ] **Run the codegen from the project root** (the server must be running for this to work — start it first if it isn't):

  ```bash
  npm run gen-openapi
  ```

  Expected: no errors; files under `frontend/src/queries/internal/` and `frontend/src/queries/integrations/v1/` are updated.

- [ ] **Verify the new hooks are available:**

  ```bash
  grep -n "getIntegrationQuery\|listIntegrationTokensQuery\|useCreateIntegrationToken\|useDeleteIntegrationToken\|useEditIntegration" frontend/src/queries/internal/internalComponents.ts | head -20
  ```

  Expected: all five names appear.

- [ ] **Commit:**

  ```bash
  git add frontend/src/queries/
  git commit -m "chore: regenerate frontend query client"
  ```

---

### Task 9: Add Integrations navbar link

**Files:**
- Modify: `frontend/src/routes/__root.tsx`

- [ ] **Add the Integrations `NavbarItem` before the Currencies one in `__root.tsx`:**

  ```tsx
  <NavbarItem>
    <Link to="/integrations" color="foreground">
      Integrations
    </Link>
  </NavbarItem>
  <NavbarItem>
    <Link to="/currencies" color="foreground">
      Currencies
    </Link>
  </NavbarItem>
  ```

- [ ] **Commit:**

  ```bash
  git add frontend/src/routes/__root.tsx
  git commit -m "feat: add Integrations navbar link"
  ```

---

### Task 10: Create the integrations list page

**Files:**
- Create: `frontend/src/routes/integrations/index.tsx`

- [ ] **Create `frontend/src/routes/integrations/index.tsx`:**

  ```tsx
  import { Button } from '@heroui/react';
  import { createFileRoute } from '@tanstack/react-router';

  import { Link } from '@/components/link';
  import { queryClient } from '@/lib/query';
  import { useStore } from '@/lib/state';
  import {
    listIntegrationsQuery,
    useSuspenseListIntegrations,
  } from '@/queries/internal/internalComponents';

  export const Route = createFileRoute('/integrations/')({
    component: RouteComponent,
    loader: () =>
      queryClient.ensureQueryData(
        listIntegrationsQuery({ queryParams: { manageable: true } }),
      ),
  });

  function RouteComponent() {
    const { data: integrations } = useSuspenseListIntegrations({
      queryParams: { manageable: true },
    });
    const user = useStore((state) => state.user);

    return (
      <div>
        <div className="flex flex-row justify-between">
          <h1 className="text-xl font-bold">Integrations</h1>
          {user && (
            <Button as={Link} to="/integrations/create">
              Create Integration
            </Button>
          )}
        </div>
        <div>
          {integrations.map((integration) => (
            <div key={integration.id}>
              <Link
                to="/integrations/$integrationId/manage"
                params={{ integrationId: integration.id }}
                color="foreground"
              >
                <span className="font-semibold">{integration.name}</span>
                {integration.description && (
                  <span className="text-default-500 ml-2 text-sm">
                    {integration.description}
                  </span>
                )}
              </Link>
            </div>
          ))}
          {integrations.length === 0 && (
            <p className="text-default-400 w-full text-center italic">
              No integrations yet.
            </p>
          )}
        </div>
      </div>
    );
  }
  ```

- [ ] **Verify the page renders** by navigating to `http://localhost:5173/integrations` (run `npm run dev` if not already running). Confirm an empty list with "No integrations yet." and a "Create Integration" button when logged in.

- [ ] **Commit:**

  ```bash
  git add frontend/src/routes/integrations/index.tsx
  git commit -m "feat: add integrations list page"
  ```

---

### Task 11: Create the integration management page

**Files:**
- Create: `frontend/src/routes/integrations/$integrationId/manage.tsx`

- [ ] **Create `frontend/src/routes/integrations/$integrationId/manage.tsx`:**

  ```tsx
  import { Alert, Button, Form, Input, Modal, ModalBody, ModalContent, ModalFooter, ModalHeader } from '@heroui/react';
  import { useForm } from '@tanstack/react-form';
  import { createFileRoute } from '@tanstack/react-router';
  import { useState } from 'react';
  import z from 'zod';

  import { queryClient } from '@/lib/query';
  import {
    getIntegrationQuery,
    listIntegrationTokensQuery,
    useCreateIntegrationToken,
    useDeleteIntegrationToken,
    useEditIntegration,
    useSuspenseGetIntegration,
    useSuspenseListIntegrationTokens,
  } from '@/queries/internal/internalComponents';
  import type {
    ErrorResponseSchema,
    IntegrationTokenSchema,
  } from '@/queries/internal/internalSchemas';
  import {
    CreateIntegrationTokenSchemaZod,
    EditIntegrationSchemaZod,
  } from '@/queries/internal/internalSchemas.zod';

  export const Route = createFileRoute('/integrations/$integrationId/manage')({
    component: RouteComponent,
    loader: ({ params: { integrationId } }) =>
      Promise.all([
        queryClient.ensureQueryData(
          getIntegrationQuery({ pathParams: { integrationId } }),
        ),
        queryClient.ensureQueryData(
          listIntegrationTokensQuery({ pathParams: { integrationId } }),
        ),
      ]),
  });

  function EditIntegrationDetails({ integrationId }: { integrationId: string }) {
    const { data: integration } = useSuspenseGetIntegration({
      pathParams: { integrationId },
    });
    const { mutateAsync: editIntegration, isPending, data } = useEditIntegration();

    async function handleSubmit(
      value: z.infer<typeof EditIntegrationSchemaZod>,
    ) {
      try {
        await editIntegration({ pathParams: { integrationId }, body: value });
        await queryClient.invalidateQueries(
          getIntegrationQuery({ pathParams: { integrationId } }),
        );
      } catch (error) {
        form.setErrorMap({
          onSubmit: {
            fields: {},
            form: (error as ErrorResponseSchema).detail,
          },
        });
      }
    }

    const form = useForm({
      defaultValues: {
        name: integration.name,
        description: integration.description,
        url: integration.url ?? '',
      } as z.infer<typeof EditIntegrationSchemaZod>,
      onSubmit: ({ value }) => handleSubmit(value),
      validators: { onSubmit: EditIntegrationSchemaZod },
    });

    return (
      <div>
        <h2 className="text-2xl font-semibold">Edit Integration Details</h2>
        <Form
          onSubmit={(e) => {
            e.preventDefault();
            form.handleSubmit();
          }}
        >
          <form.Field
            name="name"
            children={(field) => (
              <Input
                name={field.name}
                isRequired
                label="Name"
                value={field.state.value}
                onBlur={field.handleBlur}
                onChange={(e) => field.handleChange(e.target.value)}
                validationBehavior="aria"
                errorMessage={field.state.meta.errors
                  .filter((e) => e !== undefined)
                  .map((e) => e.message)
                  .join(', ')}
                isInvalid={!field.state.meta.isValid}
              />
            )}
          />
          <form.Field
            name="description"
            children={(field) => (
              <Input
                name={field.name}
                isRequired
                label="Description"
                value={field.state.value}
                onBlur={field.handleBlur}
                onChange={(e) => field.handleChange(e.target.value)}
                validationBehavior="aria"
                errorMessage={field.state.meta.errors
                  .filter((e) => e !== undefined)
                  .map((e) => e.message)
                  .join(', ')}
                isInvalid={!field.state.meta.isValid}
              />
            )}
          />
          <form.Field
            name="url"
            children={(field) => (
              <Input
                name={field.name}
                label="URL"
                value={field.state.value || ''}
                onBlur={field.handleBlur}
                onChange={(e) => field.handleChange(e.target.value)}
                validationBehavior="aria"
                errorMessage={field.state.meta.errors
                  .filter((e) => e !== undefined)
                  .map((e) => e.message)
                  .join(', ')}
                isInvalid={!field.state.meta.isValid}
              />
            )}
          />
          <Button type="submit" isLoading={isPending}>
            Save
          </Button>
          <form.Subscribe
            selector={(state) => state.errors.filter((e) => typeof e === 'string')}
            children={(errors) =>
              errors.length > 0 && <Alert color="danger">{errors}</Alert>
            }
          />
          {data && <Alert color="success">Integration updated!</Alert>}
        </Form>
      </div>
    );
  }

  function TokenRow({
    token,
    integrationId,
    onDeleteError,
  }: {
    token: IntegrationTokenSchema;
    integrationId: string;
    onDeleteError: (message: string) => void;
  }) {
    const { mutateAsync: deleteToken } = useDeleteIntegrationToken();

    async function handleDelete() {
      try {
        await deleteToken({
          pathParams: { integrationId, tokenId: token.id },
        });
        await queryClient.invalidateQueries(
          listIntegrationTokensQuery({ pathParams: { integrationId } }),
        );
      } catch (error) {
        onDeleteError((error as ErrorResponseSchema).detail);
      }
    }

    return (
      <div className="flex w-full items-center justify-between">
        <span>{token.name}</span>
        <Button color="danger" onPress={handleDelete}>
          Delete
        </Button>
      </div>
    );
  }

  function ManageTokens({ integrationId }: { integrationId: string }) {
    const { data: tokens } = useSuspenseListIntegrationTokens({
      pathParams: { integrationId },
    });
    const { mutateAsync: createToken, isPending } = useCreateIntegrationToken();

    const [showCreateForm, setShowCreateForm] = useState(false);
    const [newTokenValue, setNewTokenValue] = useState<string | null>(null);
    const [deleteError, setDeleteError] = useState<string | null>(null);

    async function handleCreateSubmit(
      value: z.infer<typeof CreateIntegrationTokenSchemaZod>,
    ) {
      try {
        const result = await createToken({
          pathParams: { integrationId },
          body: value,
        });
        setShowCreateForm(false);
        form.reset();
        await queryClient.invalidateQueries(
          listIntegrationTokensQuery({ pathParams: { integrationId } }),
        );
        setNewTokenValue(result.token);
      } catch (error) {
        form.setErrorMap({
          onSubmit: {
            fields: {},
            form: (error as ErrorResponseSchema).detail,
          },
        });
      }
    }

    const form = useForm({
      defaultValues: { name: '' } as z.infer<
        typeof CreateIntegrationTokenSchemaZod
      >,
      onSubmit: ({ value }) => handleCreateSubmit(value),
      validators: { onSubmit: CreateIntegrationTokenSchemaZod },
    });

    return (
      <div className="space-y-2">
        <h2 className="text-2xl font-semibold">Manage Tokens</h2>

        {deleteError && (
          <Alert color="danger" onClose={() => setDeleteError(null)}>
            {deleteError}
          </Alert>
        )}

        <div className="space-y-1">
          {tokens.length === 0 ? (
            <p className="text-default-400 w-full text-center italic">
              No tokens yet.
            </p>
          ) : (
            tokens.map((token) => (
              <TokenRow
                key={token.id}
                token={token}
                integrationId={integrationId}
                onDeleteError={setDeleteError}
              />
            ))
          )}
        </div>

        <Button
          onPress={() => {
            setShowCreateForm((v) => !v);
            form.reset();
          }}
        >
          Create Token
        </Button>

        {showCreateForm && (
          <Form
            onSubmit={(e) => {
              e.preventDefault();
              form.handleSubmit();
            }}
          >
            <form.Field
              name="name"
              children={(field) => (
                <Input
                  name={field.name}
                  isRequired
                  label="Token Name"
                  value={field.state.value}
                  onBlur={field.handleBlur}
                  onChange={(e) => field.handleChange(e.target.value)}
                  validationBehavior="aria"
                  errorMessage={field.state.meta.errors
                    .filter((e) => e !== undefined)
                    .map((e) => e.message)
                    .join(', ')}
                  isInvalid={!field.state.meta.isValid}
                />
              )}
            />
            <Button type="submit" isLoading={isPending}>
              Create
            </Button>
            <form.Subscribe
              selector={(state) =>
                state.errors.filter((e) => typeof e === 'string')
              }
              children={(errors) =>
                errors.length > 0 && <Alert color="danger">{errors}</Alert>
              }
            />
          </Form>
        )}

        <Modal
          isOpen={newTokenValue !== null}
          onClose={() => setNewTokenValue(null)}
        >
          <ModalContent>
            <ModalHeader>Token Created</ModalHeader>
            <ModalBody>
              <Alert color="warning">
                This token will not be shown again. Copy it now.
              </Alert>
              <Input
                isReadOnly
                label="Token"
                value={newTokenValue ?? ''}
                onClick={(e) => (e.target as HTMLInputElement).select()}
              />
            </ModalBody>
            <ModalFooter>
              <Button onPress={() => setNewTokenValue(null)}>Done</Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      </div>
    );
  }

  function RouteComponent() {
    const { integrationId } = Route.useParams();

    return (
      <div className="space-y-8">
        <EditIntegrationDetails integrationId={integrationId} />
        <ManageTokens integrationId={integrationId} />
      </div>
    );
  }
  ```

- [ ] **Verify the page builds without TypeScript errors:**

  ```bash
  npm run build
  ```

  Expected: no type errors.

- [ ] **Manually verify the management page works** by creating an integration, navigating to `/integrations/{id}/manage`, editing details, creating a token (modal should appear with copyable value), and deleting a token.

- [ ] **Commit:**

  ```bash
  git add frontend/src/routes/integrations/\$integrationId/
  git commit -m "feat: add integration management page"
  ```

---

### Task 12: Redirect `/integrations/create` after creation

**Files:**
- Modify: `frontend/src/routes/integrations/create.tsx`

- [ ] **Update `create.tsx` to import `useNavigate` and redirect after creation instead of showing a success alert.**

  Replace the `handleSubmit` function and remove the success alert:

  ```tsx
  import { Alert, Button, Form, Input } from '@heroui/react';
  import { useForm } from '@tanstack/react-form';
  import { Link, createFileRoute, useNavigate } from '@tanstack/react-router';
  import z from 'zod';

  import { queryClient } from '@/lib/query';
  import { useStore } from '@/lib/state';
  import {
    listIntegrationsQuery,
    useCreateIntegration,
  } from '@/queries/internal/internalComponents';
  import { ErrorResponseSchema } from '@/queries/internal/internalSchemas';
  import { CreateIntegrationSchemaZod } from '@/queries/internal/internalSchemas.zod';

  export const Route = createFileRoute('/integrations/create')({
    component: RouteComponent,
  });

  function CreateIntegrationForm() {
    const { mutateAsync: createIntegration, isPending } = useCreateIntegration();
    const navigate = useNavigate();

    async function handleSubmit(value: z.infer<typeof CreateIntegrationSchemaZod>) {
      try {
        await createIntegration({ body: value });
        await queryClient.invalidateQueries(
          listIntegrationsQuery({ queryParams: { manageable: true } }),
        );
        navigate({ to: '/integrations' });
      } catch (error) {
        form.setErrorMap({ onSubmit: { fields: {}, form: (error as ErrorResponseSchema).detail } });
      }
    }

    const form = useForm({
      defaultValues: {
        name: '',
        description: '',
      } as z.infer<typeof CreateIntegrationSchemaZod>,
      onSubmit: ({ value }) => handleSubmit(value),
      validators: { onSubmit: CreateIntegrationSchemaZod },
    });

    return (
      <Form
        onSubmit={(e) => {
          e.preventDefault();
          form.handleSubmit();
        }}
      >
        <form.Field
          name="name"
          children={(field) => (
            <Input
              name={field.name}
              isRequired
              label="Name"
              value={field.state.value}
              onBlur={field.handleBlur}
              onChange={(e) => field.handleChange(e.target.value)}
              validationBehavior="aria"
              errorMessage={field.state.meta.errors
                .filter((e) => e !== undefined)
                .map((e) => e.message)
                .join(', ')}
              isInvalid={!field.state.meta.isValid}
            />
          )}
        />

        <form.Field
          name="description"
          children={(field) => (
            <Input
              name={field.name}
              isRequired
              label="Description"
              value={field.state.value}
              onBlur={field.handleBlur}
              onChange={(e) => field.handleChange(e.target.value)}
              validationBehavior="aria"
              errorMessage={field.state.meta.errors
                .filter((e) => e !== undefined)
                .map((e) => e.message)
                .join(', ')}
              isInvalid={!field.state.meta.isValid}
            />
          )}
        />

        <form.Field
          name="url"
          children={(field) => (
            <Input
              name={field.name}
              label="URL"
              value={field.state.value || ''}
              onBlur={field.handleBlur}
              onChange={(e) => field.handleChange(e.target.value)}
              validationBehavior="aria"
              errorMessage={field.state.meta.errors
                .filter((e) => e !== undefined)
                .map((e) => e.message)
                .join(', ')}
              isInvalid={!field.state.meta.isValid}
            />
          )}
        />

        <Button type="submit" isLoading={isPending}>
          Create Integration
        </Button>

        <form.Subscribe
          selector={(state) => state.errors.filter((e) => typeof e === 'string')}
          children={(errors) => errors.length > 0 && <Alert color="danger">{errors}</Alert>}
        />
      </Form>
    );
  }

  function RouteComponent() {
    const user = useStore((store) => store.user);

    if (!user) {
      return (
        <div>
          Please{' '}
          <Link
            className="hover:text-primary underline transition-colors"
            to="/auth/login"
            search={{ next: '/integrations/create' }}
          >
            log in
          </Link>{' '}
          to create an integration.
        </div>
      );
    }

    return <CreateIntegrationForm />;
  }
  ```

- [ ] **Verify the build passes:**

  ```bash
  npm run build
  ```

- [ ] **Manually verify** that creating an integration redirects to `/integrations/` and the new integration appears in the list.

- [ ] **Commit:**

  ```bash
  git add frontend/src/routes/integrations/create.tsx
  git commit -m "feat: redirect to integrations list after creation"
  ```

---

### Final verification

- [ ] **Run a full build to confirm no type errors remain:**

  ```bash
  npm run build
  ```

- [ ] **Run the linter:**

  ```bash
  uv run ruff check hyperioncs/
  ```

  Expected: no errors.
