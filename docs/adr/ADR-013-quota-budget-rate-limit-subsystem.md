# ADR-013: Quota, Budget, and Rate-Limit Subsystem

**Status:** Accepted (stakeholder sign-off, 2026-07-18)

## Context
FR-21/FR-26 (quotas, budgets, rate limits, tunable defaults, OQ-9 exhaustion semantics, A-29 in-flight overrun), project-context §4 (enforcement at the adapter layer, not UI). V3 seam (d): generic over generation types — student-triggered generation later must be a policy row, not a new subsystem.

## Decision
One **governance subsystem**, three policy kinds over one vocabulary — every governed operation is an `action_type` (`lesson_generation`, `block_regeneration`, `diagram_request`, `tts_generation` (publish-time, teacher-attributed — added 2026-07-18), … future types are rows, not code):

- **Quota** (countable cap): `(tenant, action_type, scope: tenant|user, period, limit)` — e.g. diagram 20/Student/day (OQ-2 default).
- **Rate limit** (temporal throttle): `(action_type, scope: user, window, max)` — platform defaults overridable per tenant (OQ-2); guards *LLM spend*, so cache hits never charge (FR-21).
- **Budget** (monetary, calendar month): per-tenant ceiling in USD, settled from Cost Telemetry.

Mechanics:
- **Reserve → settle:** before any LLM call, the adapter path checks rate limit + quota + budget headroom and records a reservation (estimated cost); after the call it settles with the real telemetry cost. A failed job's real spend still settles (A-29). Default per-tenant generation concurrency is **1**, so the budget overrun bound is exactly one in-flight job — A-29's letter; raising concurrency (config) raises the bound correspondingly and is flagged as such where it is changed.
- Counters are PostgreSQL rows (tenant-scoped, RLS-covered) updated transactionally — no separate counting store; monthly periods key on `YYYY-MM` in the tenant's configured timezone (default Africa/Lagos).
- **Exhaustion semantics (OQ-9, verbatim behavior):** budget exhausted → `generation` queue intake pauses for the tenant (explicit Teacher-facing banner state served in Authoring bootstrap), Diagram Requests degrade to **cache-only** (`budget_paused` status with humane copy), replay of Published Versions is untouched (its path contains zero governed calls — that is the structural SM-4 claim). Every rejection emits its FR-27 event (SM-C3 feeds on these).
- Config: platform defaults + per-tenant overrides in tenant config (`$2` per-lesson soft alert emits `cost_alert` event; Operator-set monthly budgets; all values hot-changeable, no redeploy — A-14 discipline).
- Feature flags ride the same tenant-config table: `feature.diagrams`, `feature.simulation_blocks` at minimum (A-14), evaluated at generation intake and playback bootstrap.

## Consequences
- Student-triggered simulation generation in V3 = one new `action_type` row + policy values; the enforcement path already exists (seam d demonstrated).
- Cost Telemetry is the budget's source of truth — the same instrument that drives ADR-002 re-runs and the §3 migration trigger; no second accounting system.
- Per-user rate limits apply to Teachers too (FR-26: one Teacher cannot exhaust a tenant budget unthrottled).
