# ADR-008: Tenant Isolation Enforcement

**Status:** Proposed (pending stakeholder sign-off, architecture run 2026-07-17)

## Context
I-4 / project-context §4 [HARD]: every query, cache key, asset path, log line, and quota is Tenant-scoped; no cross-tenant path exists, including in admin tooling, outside explicit operator-role endpoints. ~60 tenants, one deployment.

## Decision
Single PostgreSQL database, shared schema, `tenant_id` column on every tenant-owned table — with **two independent enforcement layers**:

1. **Application layer:** every authenticated request resolves a `TenantContext` (from the session/token — never from request parameters) before any data access; repository constructors require it; there is no tenant-optional query API in the codebase. Structured-logging middleware binds `tenant_id` + user pseudonym to every log line (project-context §4).
2. **Database layer (defense-in-depth):** PostgreSQL Row-Level Security on all tenant-owned tables, keyed to a per-request session GUC (`SET LOCAL app.tenant_id = …`) set by the DB session factory from the same `TenantContext`. The app role cannot bypass RLS; a forgotten `WHERE tenant_id` returns nothing instead of everything.

- Asset paths: `tenants/{tenant_id}/…` prefixes only (ADR-012); path construction goes through one helper that requires `TenantContext`.
- Cache keys (diagram cache, idempotency fingerprints): prefixed `t:{tenant_id}:` by the same discipline; they are PostgreSQL rows, so RLS covers them too.
- CORS: allowed origins resolved per tenant from tenant config; no wildcard anywhere including error paths.
- **Operator surface (A-2):** a separate router (`/operator/*`) requiring the operator role (platform-level credential, not tenant credentials), where every endpoint takes an explicit `tenant_id` parameter and emits an audited `operator_action` event. Operator sessions use a distinct RLS-exempt DB role whose use is confined to that router — the "explicit operator-role endpoints" carve-out, auditable by construction. MVP form: CLI + minimal internal HTTP endpoints (no polished admin UI), consistent with A-2.

## Consequences
- Unit tests for isolation are mandatory (project-context §7): a fixture suite asserts RLS denies cross-tenant reads for the app role on every tenant-owned table (schema-migration CI gate — a new table without an RLS policy fails CI).
- RLS costs a few percent on hot queries — irrelevant at this scale; correctness wins.
- Tenant deletion/offboarding is a future operator workflow; rows and asset prefixes make it tractable (not built in MVP).
