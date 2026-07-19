# ADR-007: Simulation Sandboxing, Dual Mode, and Pre-Publish Checks

**Status:** Accepted (stakeholder sign-off, 2026-07-18)

## Context
FR-17 [HARD sandbox], A-35 (extend, don't narrow), OQ-5 (free-code vs template library — both modes must coexist), UX keyboard-operability extension, bounded-readiness watchdog.

## Decision
- **Sandbox:** `<iframe sandbox="allow-scripts">` — never `allow-same-origin` — with `srcdoc`-injected content carrying `<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'">`. No network, no storage, no parent access beyond postMessage. The simulation document is assembled by the Player from the Block payload; it never loads remote resources.
- **postMessage protocol v1** (versioned, documented in `/schema` alongside the Block definition): `sim:hello` → host `host:init {params, protocolVersion}` → `sim:ready` → `sim:state {…}` / `host:set-param {…}` / `sim:error {…}`. Origin-checked (`event.source` identity since sandboxed frames are opaque-origin), message-schema-validated host-side. Readiness watchdog: no `sim:ready` within 10 s (config) → Poster fallback card, quiet (a hard-crashed sandbox emits nothing — the bounded wait is the detection, per UX).
- **Dual mode in the schema (OQ-5 seam):** `simulation.mode: "template" | "freecode"`. `template` = `{templateId, params}` resolved against a platform-owned, versioned parameterised template library (each template is a reviewed, hand-written simulation document); `freecode` = `{bundleRef, params}` pointing at pipeline-generated code stored as an asset (field names camelCase per the Lesson Script casing convention). `params` is the **descriptor array** pinned in the /schema protocol document: `[{id, label, type, min, max, step, default}]`. Both render through the identical sandbox + protocol — no schema or Player change between modes. **OQ-5 ruling (stakeholder, 2026-07-18): the template library is the launch default regardless of benchmark outcome**; free-code activates behind the tenant flag only after clearing ADR-002's ≥ 70% check-pass gate. **Template-driven simulations are demo-critical: the template seed set is a first-class M5 deliverable, not deferred polish.**
- **Poster capture:** the check harness screenshots the simulation at `sim:ready` — that capture *is* the Simulation Block's poster (deterministic, from the content itself, never AI-generated imagery), regenerated whenever the Block is regenerated.
- **Pre-publish checks (A-35 extended):** run server-side at publish (and at Block Regeneration) in headless Chromium via Playwright against the real sandbox document: (1) loads without uncaught error; (2) `sim:ready` within budget; (3) every declared param maps to a native form control or focusable role with key handlers (keyboard-operability, UX A-35 extension) — asserted by DOM inspection inside the frame; (4) responds to `host:set-param` for each declared param; (5) resource budget: bundle ≤ 1.5 MB, heap ≤ 128 MB, no main-thread task > 1 s during a 15 s scripted interaction. Any failure blocks publish with the per-Block readable reason (A-11); results are stored on the Draft.

## Consequences
- Publish latency includes a headless check run (seconds, not minutes; checks run per changed Simulation Block only).
- The template library is a new curated internal asset class (like the Model Library): versioned, licence-clean, platform-owned — seeded as part of the Simulation epic.
- Player-side the two modes are indistinguishable — students and the Review Gate see one Simulation Block.
