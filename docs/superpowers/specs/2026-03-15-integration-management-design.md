# Integration Management Feature Design

**Date:** 2026-03-15
**Branch:** integration-management

## Overview

Add comprehensive integration management to the HyperionCS app: a list page for integrations the user owns, a management page for editing metadata and managing tokens, and token name support.

## Data Model

### `IntegrationToken`
Add a `name: Mapped[str]` column. Requires a new Alembic migration.

No other model changes are needed.

## Backend API

All new endpoints live in the existing integrations router (`hyperioncs/api/app/routers/integrations.py`). All require the user to have the `Edit` role (`IntegrationRole.Owner`) on the integration.

### Extend existing list endpoint
- `GET /integrations/?manageable=true` — add an optional boolean query param. When `true`, filters to integrations where the current user has an Edit role. When absent or `false`, existing behavior is preserved (public integrations + integrations the user can connect).

### New single-integration endpoints
- `GET /integrations/{id}` — returns a single integration the current user has Edit access to.
- `PUT /integrations/{id}` — updates `name`, `description`, and `url`. Requires Edit role.

### Token endpoints
- `GET /integrations/{id}/tokens` — lists tokens for an integration. Response includes `id` and `name` only; the token value is never returned here.
- `POST /integrations/{id}/tokens` — creates a token with a `name`. Returns `id`, `name`, and `token` (the raw token value). This is the only time the token value is ever returned.
- `DELETE /integrations/{id}/tokens/{token_id}` — deletes a token. Requires Edit role on the integration.

### Response schemas
- `IntegrationTokenSchema`: `id`, `name` — used for list responses.
- `CreatedIntegrationTokenSchema`: `id`, `name`, `token` — used only for the create response.

## Frontend

### `/integrations/` (new)
List page for integrations the user can manage. Matches the structure of the currencies list page:
- Header row with "Integrations" title and a "Create Integration" button (visible only when logged in).
- List of integrations, each showing name and description, linking to `/integrations/$id/manage`.
- Data fetched via `listIntegrationsQuery` with `manageable: true`.

### `/integrations/$id/manage` (new)
Management page with two sections, following the pattern of `/currencies/$shortcode/manage`:

**Edit Integration Details**
- Form pre-populated with `name`, `description`, and `url`.
- On save, calls `PUT /integrations/{id}` and invalidates the integration query.
- `private` is not editable here (reserved for future admin functionality).

**Manage Tokens**
- List of existing tokens showing name only, each with a "Delete" button.
- "Create Token" button reveals an inline form with a `name` field and a submit button.
- On successful creation, a modal appears containing:
  - The token value in a copyable display.
  - A warning that the value will not be shown again.
  - A dismiss button.

### `/integrations/create` (modified)
After successful creation, redirect to `/integrations/` instead of showing a static success alert, so the user lands on the list with their new integration visible.

## Error Handling

- 403 if user lacks Edit role on the integration (get, edit, token operations).
- 404 if integration does not exist.
- Follows existing error handling patterns (JSONResponse with `ErrorResponseSchema`).

## Out of Scope

- Editing the `private` flag (future admin feature).
- Renaming tokens after creation.
- Viewing token values after initial creation.
