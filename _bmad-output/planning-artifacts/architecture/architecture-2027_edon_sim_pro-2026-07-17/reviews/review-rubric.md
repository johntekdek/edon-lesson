# Rubric Review — Architecture Spine (e-DON Lesson Studio)

**Artifact:** `_bmad-output/planning-artifacts/architecture/architecture-2027_edon_sim_pro-2026-07-17/ARCHITECTURE-SPINE.md`
**Companions read:** `docs/adr/ADR-001..014`, `docs/integrations/*.md`, PRD + addendum, UX EXPERIENCE.md handoff section, project-context.md
**Reviewer:** rubric walker | **Date:** 2026-07-17

**Gate verdict: PASS WITH CONDITIONS** — the spine is unusually complete and its rules are overwhelmingly mechanical, but two High findings (a licence-relevant tech contradiction in ADR-006 and an undefined operator credential that contradicts AD-14's closed enumeration) must be fixed before epics fan out.

**Counts:** Critical 0 · High 2 · Medium 4 · Low 6

---

## Findings

### Critical

None.

### High

| ID | Finding | Location | Fix |
| --- | --- | --- | --- |
| H1 | ADR-006 mandates Draco compression "via `@gltf-transform/cli`" — the exact binary the spine Stack table and ADR-012 **exclude** as Prosperity-PPL dual-licensed (§5 [HARD] violation if followed). A story agent implementing Model3D ingest from ADR-006 introduces a forbidden dependency. | `docs/adr/ADR-006-player-embedding-and-bundles.md` (Asset budgets bullet) vs spine Stack row `@gltf-transform` + ADR-012 | Edit ADR-006 to read "via the MIT `@gltf-transform` SDK packages from our ingest script (ADR-012); CLI excluded per §5". |
| H2 | Operator authentication is undefined and contradicts the spine's own closed set: AD-14 declares "exactly four credential kinds in MVP" (none authenticates the operator), yet AD-6/ADR-008 require an operator-role router with a "platform-level credential" in MVP. The Deferred row covers operator *tooling form*, not its credential. Two agents building the operator surface will invent divergent auth. | Spine AD-14 vs AD-6; `docs/adr/ADR-008` (Operator surface) / `ADR-009` (role model lists `operator` with no credential kind) | Add the operator credential as a fifth enumerated kind in AD-14 (or define it explicitly in ADR-009 and cite it from AD-14's enumeration). |

### Medium

| ID | Finding | Location | Fix |
| --- | --- | --- | --- |
| M1 | Lesson Script JSON casing convention is `camelCase`, but ADR-007 defines Simulation Block schema fields as `mode`, `{template_id, params}`, `{bundle_ref, params}` — snake_case inside the keystone contract; the schema author and the Player author can legitimately diverge. | Spine Consistency Conventions "JSON field casing" vs `docs/adr/ADR-007` (Dual mode) | Rename ADR-007's schema fields to `templateId`/`bundleRef` (or carve an explicit exception in the casing row). |
| M2 | Authoring SPA internal composition — routing, data-fetching, client-state conventions — is neither decided, deferred, nor an open question. The SPA spans multiple surfaces (course home, generate, review workspace, queue) that independent story agents will build; router/fetch-layer choices will fork. | Spine Structural Seed `authoring/`; Deferred table (absent) | Add one convention row (or Deferred row with a working assumption, e.g. "react-router + plain fetch wrappers, no state library") for Authoring SPA composition. |
| M3 | Mandatory testing floors name no unit-test runner or lint/format toolchain (pytest? vitest? ruff? eslint/prettier?) — Playwright is the only test tool in the Stack, and project-context is silent too. Every story ships tests; per-story tool divergence is near-certain. | Spine Consistency Conventions "Testing floors" + Stack table | Name the runners and lint/format tools in the Stack table (test-runner choice is exactly the kind of cross-unit constant the spine owns). |
| M4 | NFR-7's permissive-licence rule is enforced only by case-by-case exclusions (MinIO, gltf CLI) — no general mechanical gate exists, so the next agent adding a copyleft transitive dependency has nothing to fail against. | Spine Stack notes; Capability Map (NFR-7 unmapped); project-context §5 | Add a licence-audit CI convention (e.g. allowlist check on lockfiles) to the Consistency Conventions table. |

### Low

| ID | Finding | Location | Fix |
| --- | --- | --- | --- |
| L1 | Source-tree comment says "ADR-001..ADR-013 (this run)" but 14 ADRs exist (frontmatter and AD-10 cite ADR-014). | Spine Structural Seed, `docs/adr/` line | Update the comment to ADR-014. |
| L2 | Platform API list/pagination conventions unspecified — lesson picker and outbox both return lists (`limit=100` appears once); offset-vs-cursor could diverge per endpoint. | Consistency Conventions; `docs/integrations/mod-edonlesson-platform-api.md` §2.1/2.4 | Add one line fixing the list convention (e.g. `limit` + opaque cursor). |
| L3 | AD-20 (externalised strings) is the only AD whose Rule names no mechanical check — no hardcoded-string lint, unlike the sibling no-TS gate. | Spine AD-20 | Name the enforcement (i18n lint rule or CI grep gate) in the Rule. |
| L4 | Release/deploy mechanism (how a build reaches the VPS; downtime posture) is neither decided nor in the Deferred table — only a `runbooks/deploy` placeholder implies it. | Spine Deployment & environments; Deferred table | Add a Deferred row ("deploy mechanics — runbook + CI provider decision, first epic"). |
| L5 | Integration doc claims the playback token is "device-bound to the session" — no binding mechanism exists in AD-14/ADR-009 (which describe an opaque bearer). Overclaims the contract. | `docs/integrations/mod-edonlesson-platform-api.md` §2.3 | Drop "device-bound" or define the binding in ADR-009. |
| L6 | i18n catalog Deferred row assumes "key-value JSON" but fixes no key-naming convention; Player and Authoring units externalising strings before the first localisation story could diverge on key structure. | Spine Deferred table, i18n row | State the key convention (e.g. `surface.component.slug`) in the working assumption. |

---

## Per-Dimension Verdicts

| # | Dimension | Verdict | Notes |
| --- | --- | --- | --- |
| 1 | Fixes the real divergence points, misses none | **Adequate** | The hunt found real misses: operator credential (H2), Authoring SPA internals (M2), test/lint tooling (M3), API list conventions (L2). Everything else independent agents need — schema dialect, casing, error shape, event taxonomy, attempt semantics, tenancy, storage keys, budgets — is nailed down with unusual thoroughness. |
| 2 | Every AD Rule enforceable and divergence-preventing | **Strong** | Nearly every AD names its mechanical check: import-linter contract (AD-1), CI fixture equivalence (AD-2), no-UPDATE/DELETE grants (AD-5), RLS-per-migration CI (AD-6), budgets.json CI hard fail (AD-11), headless pre-publish checks (AD-12), unit-tested telemetry row contract (AD-19). AD-20 is the lone rule without a named check (L3). Each Prevents line genuinely matches its Rule. |
| 3 | Nothing under Deferred can cause divergence | **Strong** | All ten rows checked: each is content, ops tooling, or config behind an already-fixed mechanism (registry, port, policy row), with a named revisit point. Only the i18n key convention (L6) has any residual divergence surface, and the working assumption mostly covers it. |
| 4 | Named tech internally consistent across spine + ADRs | **Adequate** | Versions align everywhere checked (FastAPI 0.139.x, Procrastinate 3.9.x, Playwright 1.61, Three r185, Vite 8, React 19.2, sim budgets 1.5 MB/128 MB, CI profile 6×/400 kbps/1.5 GB). Two real contradictions: the gltf-transform CLI (H1) and Simulation schema field casing (M1). Web verification of external claims is the other lens's job. |
| 5 | The PRD drove it — Capability Map coverage | **Strong** | All of FR-1..29 map to a home and governing ADs; I-1..4 each land structurally (replay path zero-LLM, review gate via publish transaction, schema package, TenantContext law); UX handoff items 2, 10, 11, 12, 15, 16, 17 and amendment E all traced into ADs 2/7/13/14/15/17. NFR-7's missing mechanical gate (M4) is the only coverage soft spot; NFR-1 is carried by ADR-002/005 though unmapped by row. |
| 6 | Every altitude-owned dimension decided/deferred/open | **Strong** | Deployment & environments diagrammed (systemd units, dev/staging/prod), infra strategy fixed (single VPS, GPU-never rule, horizontal worker path), backup/DR decided (nightly pg_dump + rsync, drills deferred with revisit), monitoring explicitly deferred with the signals already emitted. Deploy mechanics (L4) is the one unnamed corner. |
| 7 | Diagrams valid, non-empty, structure-bearing | **Strong** | All four mermaid blocks mentally parsed clean: dependency `graph TD` (dotted labeled edge syntax valid), containers `graph LR` (subgraph titles, labeled edges valid), deployment `graph TD` (node-to-subgraph link valid), `erDiagram` (all cardinality glyphs and quoted labels valid). Each conveys real structure — layering, runtime topology, ops units, entity ownership. |
| 8 | Terse where it should be, complete where it must be | **Strong** | ~350 lines carrying 21 invariants, conventions, stack, structure, coverage map, and deferrals — every clause load-bearing, rationale pushed to ADRs. AD-11 borders on overload but each number is a genuine CI input. No padding found. |
