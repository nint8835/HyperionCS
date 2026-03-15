# Integration Management Feature Design

**Date:** 2026-03-15
**Branch:** integration-management

## Overview

Add comprehensive integration management to the HyperionCS app: a list page for integrations the user owns, a management page for editing metadata and managing tokens, and token name support.

## Data Model

### `IntegrationToken`
Add a `name: Mapped[str]` column. Requires a new Alembic migration.

**Migration strategy:** There is no existing data in `integration_tokens`. Amend the existing `integration_tokens` migration (rather than creating a new one) to include the `name` column from the start.

### `IntegrationRole` / `IntegrationActionRoles`
Add a new `View = "view"` value to `IntegrationRole` and a corresponding `IntegrationActionRoles.View = [IntegrationRole.View, IntegrationRole.Owner]` action role list. This represents the minimum role required to view a private integration's details.

No other model changes are needed.

## Frontend Client Regeneration

After all backend changes are complete, the frontend query client must be regenerated before writing frontend code:

```
npm run gen-openapi
```

This will update all generated files under `frontend/src/queries/` — including adding `queryParams` support to `listIntegrationsQuery`, generating new queries for the token endpoints and `getIntegrationQuery`, and updating all Zod schemas.

**Query key note:** After regeneration, `listIntegrationsQuery({})` and `listIntegrationsQuery({ queryParams: { manageable: true } })` produce **different cache keys**. The existing currencies manage page calls `listIntegrationsQuery({})` (no filter) — this is intentional and should not be changed. Only the `{ queryParams: { manageable: true } }` variant is used on the new integrations pages and should be invalidated on create.

**`queryParams` is optional** in the regenerated type (FastAPI query params with defaults generate optional fields in OpenAPI). The existing `useSuspenseListIntegrations({})` call on the currencies manage page will remain valid after regeneration without modification.

**Generated hook names** are derived from the Python function names used in the backend router. The following names must be used for the new endpoints so that the generated client has predictable names:

| Python function | Generated query/hook |
|---|---|
| `get_integration` | `getIntegrationQuery`, `useSuspenseGetIntegration` |
| `edit_integration` | `useEditIntegration` |
| `list_integration_tokens` | `listIntegrationTokensQuery`, `useSuspenseListIntegrationTokens` |
| `create_integration_token` | `useCreateIntegrationToken` |
| `delete_integration_token` | `useDeleteIntegrationToken` |

## Backend API

All new endpoints live in the existing integrations router (`hyperioncs/api/app/routers/integrations.py`).

**Path parameter naming:** Use `{integration_id}` for all new endpoints, consistent with the existing `/{integration_id}/connect` and `/{integration_id}/disconnect` endpoints.

**Authentication:** All endpoints require the user to be authenticated via `require_session_user`. Unauthenticated requests raise HTTP 401.

**Authorization:** A missing integration, or an integration the user does not have the required role on, returns HTTP 403. Token-level 404s are the exception — see the delete token endpoint.

**Route declaration order:** FastAPI resolves literal paths before parameterized paths within the same method. Declare `GET /` (the existing list endpoint) before `GET /{integration_id}` to ensure the list endpoint is matched first.

### Extend existing list endpoint
- `GET /integrations/?manageable=true` — add an optional boolean query param. When `true`, filters to integrations where the current user has an Edit role (`IntegrationActionRoles.Edit`). When absent or `false`, existing behavior is preserved (public integrations + integrations the user has a Connect permission for). Authentication is required in both cases, as it is today.

  Note: `IntegrationActionRoles.Edit` and `IntegrationActionRoles.Connect` both equal `[IntegrationRole.Owner]` today. The `manageable` param is semantically distinct — it filters by intent (the user can manage this integration), not by the connect permission. If these role lists diverge in future, the behavior should remain tied to `IntegrationActionRoles.Edit`.

### New single-integration endpoints
- `GET /integrations/{integration_id}` — returns a single integration visible to the current user. Access rules mirror the existing list endpoint: public integrations are accessible to anyone (authenticated); private integrations require the user to have a View role (`IntegrationActionRoles.View`). Response model: `IntegrationSchema` (`id`, `name`, `description`, `url`, `private`). HTTP 200 on success, 403 if not found or access not permitted.
- `PATCH /integrations/{integration_id}` — updates `name`, `description`, and `url`. All three fields are required; omitting a field is an error, not a partial update. `url` has no default and **must not be given a default value in `EditIntegrationSchema`**, even though `CreateIntegrationSchema.url` uses `default=None`. Sending `url: null` or `url: ""` both clear the URL (via `NullableString`). `private` is not editable via this endpoint. Response model: `IntegrationSchema`. HTTP 200 on success, 403 if not found or no Edit role. Consistent with the existing `PATCH /currencies/{shortcode}` pattern.

### Token endpoints
- `GET /integrations/{integration_id}/tokens` — lists tokens for an integration. Response model: `list[IntegrationTokenSchema]`. The token value is never returned here. Returns 403 if the integration does not exist or the user lacks Edit role.
- `POST /integrations/{integration_id}/tokens` — creates a token. Request body: `CreateIntegrationTokenSchema`. Response model: `CreatedIntegrationTokenSchema`. HTTP 201 on success. Returns 403 if the integration does not exist or the user lacks Edit role. This is the only time the token value is ever returned. The token's `id` must be pre-generated explicitly using `id=default_uuid_str()` (consistent with the `create_integration` pattern) so that the `id` is available to build the JWT before the object is flushed to the database.
- `DELETE /integrations/{integration_id}/tokens/{token_id}` — deletes a token (`token_id: str`). The resource path `/integrations/{integration_id}/tokens/{token_id}` is treated as the full resource identifier — a token only exists at this path if it both exists and belongs to the specified integration. Authorization check order:
  1. Does the integration exist? → 403 if not.
  2. Does the user have Edit role on the integration? → 403 if not.
  3. Does a token with `token_id` exist where `integration_id` matches? → 404 if not.

  Returns HTTP 202 with an empty body on success.

### Request and response schemas

**`CreateIntegrationTokenSchema`** (request body for token creation):
- `name: str` — required.

**`EditIntegrationSchema`** (request body for `PATCH /integrations/{integration_id}`):
- `name: str` — required. No min-length validator; matches the validation level of `CreateIntegrationSchema`.
- `description: str` — required. No min-length validator; matches the validation level of `CreateIntegrationSchema`.
- `url: NullableString` — use the existing `NullableString` type (converts empty strings to `None`). **No default** (unlike `CreateIntegrationSchema.url` which has `default=None`); this field is required.

**`IntegrationTokenSchema`** (used for list responses):
- `id: str`
- `name: str`

**`CreatedIntegrationTokenSchema`** (used only for the create response, HTTP 201):
- `id: str`
- `name: str`
- `token: str` — a JWT signed with `config.jwt_secret` using `config.jwt_algorithm`, containing a `token_id` claim set to the token's `id`. Consistent with the existing `require_integration` dependency.

## Frontend

> **Before writing any frontend code**, regenerate the client with `npm run gen-openapi` as described in the Frontend Client Regeneration section above.

### Navbar
Add an "Integrations" link in `__root.tsx` pointing to `/integrations/`, placed before the existing "Currencies" link.

### `/integrations/` (new)
List page for integrations the user can manage. Matches the structure of the currencies list page:
- Header row with "Integrations" title and a "Create Integration" button (visible only when logged in, linking to `/integrations/create`).
- List of integrations, each showing name and description, linking to `/integrations/$integrationId/manage`.
- Route defines a `loader` that calls `queryClient.ensureQueryData(listIntegrationsQuery({ queryParams: { manageable: true } }))`, consistent with the pattern used in other list pages.

### `/integrations/$integrationId/manage` (new)
Management page with two sections, following the pattern of `/currencies/$shortcode/manage`. Unauthenticated users navigating directly to this page will have API calls fail with 401, consistent with how the rest of the app handles unauthenticated access to protected pages.

Route defines a `loader` that calls `queryClient.ensureQueryData` for both:
- `getIntegrationQuery({ pathParams: { integrationId } })`
- `listIntegrationTokensQuery({ pathParams: { integrationId } })`

**Edit Integration Details**
- Form pre-populated with `name`, `description`, and `url` from `getIntegrationQuery`. Since `url` may be `null`, render it as an empty string in the input (consistent with the `value={field.state.value || ''}` pattern already used in `create.tsx`).
- On save, calls `PATCH /integrations/{integration_id}` then `await queryClient.invalidateQueries(getIntegrationQuery({ pathParams: { integrationId } }))`.
- On success: show a success alert driven by the mutation `data` value (consistent with `ManageCurrencyDetails`).
- On error: call `form.setErrorMap(...)` to display the error detail, with an `Alert color="danger"` via `form.Subscribe` (consistent with the `ManageCurrencyDetails` error handling pattern).
- `private` is not shown or editable (reserved for future admin functionality).

**Manage Tokens**
- List of existing tokens from `listIntegrationTokensQuery`, showing name only, each with a "Delete" button.
- "Create Token" button reveals an inline form with a `name` field and a submit button. Clicking "Create Token" again while the form is visible collapses it (toggle behavior). The form resets each time it is opened.
- On successful creation:
  1. Capture the `token` value from the mutation response into local component state before clearing any mutation state.
  2. The inline form collapses and resets.
  3. `await queryClient.invalidateQueries(listIntegrationTokensQuery({ pathParams: { integrationId } }))` — wait for the list to refresh.
  4. A modal appears containing the token value (from local state) in a copyable display, a warning that the value will not be shown again, and a dismiss button. Dismissing the modal clears the local state — the token value is not recoverable without creating a new token.
- On delete:
  - Call `DELETE /integrations/{integration_id}/tokens/{token_id}`.
  - On success: `await queryClient.invalidateQueries(listIntegrationTokensQuery({ pathParams: { integrationId } }))`.
  - On error: show an inline error alert (consistent with the `Alert color="danger"` pattern used elsewhere).
  - Token operations do not modify the integration itself, so `getIntegrationQuery` does not need to be invalidated.

### `/integrations/create` (modified)
After successful creation:
1. `await queryClient.invalidateQueries(listIntegrationsQuery({ queryParams: { manageable: true } }))` — invalidate only this variant; `listIntegrationsQuery({})` (used on the currencies manage page) should not be invalidated here.
2. Use `useNavigate` to redirect to `/integrations/`, consistent with the pattern for post-submit navigation in the rest of the frontend.

Remove the existing `{data && <Alert color="success">Integration created!</Alert>}` line — it is unreachable after the redirect.

## Error Handling

- HTTP 401 if the user is not authenticated (raised by `require_session_user`).
- HTTP 403 if the user lacks the required role on the integration, or if the integration does not exist.
- HTTP 404 for token not found or not belonging to the specified integration on the delete endpoint.
- Follows existing error handling patterns (`JSONResponse` with `ErrorResponseSchema`).

## Out of Scope

- Editing the `private` flag (future admin feature).
- Renaming tokens after creation.
- Viewing token values after initial creation.
