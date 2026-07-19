# ADR-011: Data Protection Mechanics (NFR-9)

**Status:** Accepted (stakeholder sign-off, 2026-07-18)

## Context
NFR-9/OQ-8: identity-stripped LLM requests; pseudonymised telemetry preserving [HARD] tenant/user attribution; configurable log retention (default 12 months); record of external processors. A-15: minimum Student identifiers, no extra PII.

## Decision
- **Identity stripping is structural, not procedural:** the LLM adapter's request type has **no identity fields** — it accepts `(workload, messages, params, accounting_ref)` where `accounting_ref` is an opaque internal id resolved to tenant/pseudonym only inside the telemetry writer. Free-text user inputs (topic, guidance, diagram request text) pass through as content — the platform does not attempt PII scrubbing of free text in MVP; this boundary is documented user-facing guidance, and the request types carry nothing else. Same rule at the edon-rag client (docs/integrations/edon-rag §2).
- **Pseudonymisation:** `user_pseudonym = HMAC-SHA256(per-tenant salt, lms_user_id)` — stable per user (attribution [HARD] holds), unlinkable across tenants, computed at the identity boundary. Telemetry, events, and logs carry only the pseudonym. The raw `lms_user_id` exists in exactly two places, both required for function: the delivery outbox rows (Moodle needs the real id to write grades) and the session/attempt tables that feed them. A single documented mapping point (`identity` module) is the only code allowed to hold both.
- **Retention:** `retention.yaml` config — events and cost telemetry default **12 months**, structured logs 12 months, job progress rows 30 days, replayed-jti and expired-session rows 7 days. A nightly maintenance job (Procrastinate `maintenance` queue) enforces it; retention changes are config.
- **Processor record:** `docs/processors.md` in-repo — LLM providers (per active ADR-002 config), hosting provider, edon-rag (institutional processor). Updated when config changes providers; CI reminds via `.env.example` discipline (project-context §7).
- Student-facing content storage is minimal by construction: quiz answers and diagram request texts are the only Student-authored content stored, both tenant-scoped, both under retention.

## Consequences
- Telemetry-based analytics (future dashboard) works on pseudonyms by default — no re-identification needed for aggregates.
- Salt rotation would break pseudonym stability; salts are per-tenant, generated at tenant creation, and deliberately **not** rotated (documented).
- NDPA programme remains platform-level and out of scope (NFR-9); this ADR is the PRD-scoped mechanics only.
