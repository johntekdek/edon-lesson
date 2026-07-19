# ADR-009: Identity, Sessions, and Credentials

**Status:** Accepted (stakeholder sign-off, 2026-07-18)

## Context
FR-24, FR-29 (Launch Token — UX handoff item 16), NFR-3 (rotation from day one), playback authentication, block_edon_ai pattern consistency.

## Decision
Five credential kinds, no others:

0. **Operator credentials** (internal): named per-operator keys, hashed at rest like tenant keys, issued/revoked via server CLI, dual-valid for rotation, accepted **only** on the `/operator/*` router (ADR-008); every authenticated operator request emits the audited `operator_action` event. No operator UI login exists in MVP (CLI + minimal endpoints per A-2).

1. **Tenant API keys** (plugin → platform, server-to-server): random 256-bit, hashed at rest (SHA-256 + pepper), **two concurrently valid per tenant** so rotation is issue → switch → revoke with no downtime. Scope: the mod_edonlesson and block_edon_ai endpoints (docs/integrations/).
2. **Launch Token** (FR-29): JWT **HS256** with per-tenant signing secret (distinct from API keys; also dual-valid, `kid` header selects). Claims: `iss` (tenant), `sub` (LMS user id), `role` (`teacher` | `tenant_admin`), `course_ref`, optional `draft_hint`, `iat`, `exp = iat + 120 s`, `jti`. **Single-use:** `jti` stored until `exp`; replay → the Relaunch notice. Carried in the URL **fragment** so it never reaches server logs.
3. **Authoring Session:** minted on token exchange; server-side session row + HttpOnly `SameSite=Lax` cookie. **8 h absolute lifetime, no idle timeout** (a lecturer's working day; short enough that a shared lab machine ages out overnight). Session bootstrap tells the client `expires_at` → pre-expiry warning banner at **T-15 min**; expiry lands on the Relaunch notice. Relaunch-into-same-Draft: platform records last-active-draft per (tenant, user); a fresh valid launch redirects there when the launch course matches and pending local edits or the server record point at it. Autosave durability is independent of sessions (ADR-004 revisions + localStorage preservation of unacknowledged edits, restored after relaunch).
4. **Playback Session token** (Student): minted server-to-server (docs/integrations/mod-edonlesson §2.3); opaque bearer bound to `(tenant, user pseudonym, lesson, activity_ref, attempt context)`; 24 h validity (covers a school day + SM-3 semantics); scope limited to script fetch, view marks, quiz submission, resume state. The browser never holds tenant keys.

Role model (whole MVP): `student`, `teacher`, `tenant_admin` (Teacher powers + edit/republish any tenant lesson, OQ-13 — Review Workspace shows the owner banner), `operator` (platform-internal, ADR-008). Roles arrive from the LMS via token/session claims; the platform holds no password store and no standalone login (FR-29, PRD §8).

## Consequences
- Clock skew: plugin and platform must be NTP-sane; exchange tolerates ±30 s `iat` skew (120 s lifetime absorbs it).
- Secrets: all four kinds rotate without downtime; `.env.example` documents platform-side config. **Interpretation of §4 "secrets via environment configuration only" (flagged for sign-off):** platform-level secrets (provider API keys, DB creds, the KEK) are env-only; per-tenant material cannot live in env at ~60 tenants — tenant API keys are stored as hashes (not recoverable secrets), and per-tenant signing/edon-rag secrets are data rows encrypted with the env-held KEK. No secret is ever committed.
- Dev/staging path: a dev-only token-minting CLI drives the same JWT exchange code path (dev signing key, disabled by prod config), so every pre-Moodle epic is testable without the plugin.
- The 8 h / T-15 min / 120 s / 24 h values are config, not code (tunable per deployment; defaults recorded here).
