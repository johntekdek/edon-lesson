# Reconciliation Review — UX Spine vs Architecture

**Deliverable:** `ARCHITECTURE-SPINE.md` + `docs/adr/ADR-001..013` + `docs/integrations/*` (run 2026-07-17)
**Source of truth:** `_bmad-output/planning-artifacts/ux-designs/ux-2027_edon_sim_pro-2026-07-16/EXPERIENCE.md` (final, incl. § Rulings & Open Items + Architect handoff) and `DESIGN.md`
**Reviewer scope:** every UX requirement with an architecture implication — missing, distorted, or contradicted.

**Verdict:** the architecture landed the UX handoff remarkably completely — items 11, 16, and 17 are resolved in full, sub-clause by sub-clause. One explicit handoff item (12) is only half-resolved, and a small number of architecture-owned hooks the UX delegated by name did not land.

Counts: **1 critical / 3 high / 3 medium / 6 low.**

---

## CRITICAL

### C1. Handoff item 12 — Curriculum Reference: Teacher correction is undefined
- **UX anchor:** EXPERIENCE.md § Rulings & Open Items, item 12: "pipeline-derived; **define whether and how a Teacher corrects it during review**." Handoff list demands items 11/12/16/17 "unabridged."
- **Architecture location:** derivation landed — ADR-005 (`plan` stage: "curriculum-ref derivation"), edon-rag-retrieval.md WI-RAG-2 (topic-derived-label fallback), mod-edonlesson §2.1 (`curriculum_ref` in the picker). The correction half appears **nowhere**: no spine rule, no ADR, no editability statement, no schema/Draft field ruling. The spine's frontmatter `binds` claims item 12 is carried, so the gap is silent.
- **Fix:** rule it explicitly — e.g., `curriculum_ref` is a lesson-level Draft field, Teacher-editable in the Review Workspace (extending the A-28 map), revalidated on save, frozen into the Published Version — or record an explicit "not correctable in MVP" decision with stakeholder sign-off; either way, one sentence in AD-2/AD-5 territory plus an ADR-004/005 note.

## HIGH

### H1. Constrained-tier device-class definition — architecture-owned, absent
- **UX anchor:** EXPERIENCE.md § Capability Tiers, Constrained row: "asset too heavy for the detected device class (**definition architecture-owned**) or load fails."
- **Architecture location:** AD-11 and ADR-006 define only the Showcase detection formula and demote-to-Full. No rule anywhere defines the device classes, the per-class asset-weight threshold that lands a Model3D/Simulation Block on Constrained (poster card, no load control), or that load failure routes to Constrained behavior.
- **Fix:** add the Constrained predicate to AD-11/ADR-006 (e.g., `deviceMemory < 2` or undefined ⇒ constrained device class; asset transfer size > class threshold from `budgets.json` ⇒ Constrained rendering; any heavy-asset load/runtime failure ⇒ Constrained).

### H2. "Mark invalid" cache eviction — the operative governance rule did not land
- **UX anchor:** EXPERIENCE.md § Component Patterns, Diagram review queue row + Flow 5 + Ruling 2: "Mark invalid … clears it *and evicts its Tenant cache entry* so it can never be served again — the next equivalent Diagram Request regenerates fresh." Handoff names the event "diagram invalidated (**cache evicted**)."
- **Architecture location:** AD-7 carries the event names (`diagram_review_completed`, `diagram_invalidated`); the ERD links `DIAGRAM_CACHE ||--o{ DIAGRAM_REPORT`. But no spine rule, ADR, or contract states the eviction side-effect, the never-served-again guarantee, or the regenerate-fresh semantics (ADR-013's cache-only budget mode makes an evicted-but-budget-paused diagram's fate genuinely ambiguous).
- **Fix:** one rule in AD-7 or a `core/diagrams` note: `mark_invalid` = delete/tombstone the `DIAGRAM_CACHE` row + its stored SVG asset in the same transaction as the `diagram_invalidated` event; subsequent equivalent requests miss the cache (and in `budget_paused` mode return not-available, never the invalidated SVG).

### H3. Poster production mechanism — delegated by name, only half-landed
- **UX anchor:** EXPERIENCE.md § Capability Tiers ladder: posters are "pre-rendered views of the curated glTF asset, captures of the simulation, or SVG … **the production mechanism is architecture-owned**," and "never AI-generated illustrative raster imagery (that fence stands, PRD §8)."
- **Architecture location:** Model3D poster capture at library ingest is specified (ADR-012 ingest pipeline); the pipeline stage says only "poster selection/production" (ADR-005). No mechanism exists for **Simulation posters** (the obvious host — the ADR-007 headless-Chromium check run — is never connected to poster capture), and the no-AI-raster fence is not encoded anywhere a pipeline validator could enforce it.
- **Fix:** specify per-type production in ADR-005/007/012 — Model3D: ingest-time render capture; Simulation: screenshot from the ADR-007 headless check run at publish/regeneration; Diagram: the SVG itself — and add "posters must originate from these mechanisms, never from an image-generation workload" as an AD-17/pipeline-validator rule.

## MEDIUM

### M1. Mid-session graceful tier demotion unspecified
- **UX anchor:** EXPERIENCE.md § Capability Tiers ladder: "Demotion is graceful mid-session: if the connection degrades, the next heavy Block simply behaves like Full."
- **Architecture location:** AD-11/ADR-006 read as one-shot detection at mount; no re-evaluation point is defined.
- **Fix:** one sentence in ADR-006: tier signals (`effectiveType`, `saveData`) are re-read at each heavy-Block load decision; demotion applies per-Block, promotion never mid-session.

### M2. Text-alternative fields — poster scope and Teacher-editability not explicit
- **UX anchor:** EXPERIENCE.md Ruling 15 / § Accessibility Floor: `altText`/`longDescription` on **every Diagram Block and every poster (Model3D, Simulation)**, pipeline-populated, **Teacher-editable in review** (A-28 extension).
- **Architecture location:** sanitiser preservation is fully landed (AD-13); field names appear in the spine's JSON-casing convention and the diagram API; ADR-005 says only generic "altText population." Nothing states the fields exist on Model3D/Simulation poster payloads in Schema v1.0, nor that they are editable Draft text.
- **Fix:** in AD-2/ADR-005, enumerate the carrying payloads (diagram + model3d.poster + simulation.poster) and add "text alternatives are plain-text Draft-editable fields" so the schema work and the Block-editor endpoint carry them by contract.

### M3. Whole-lesson Regeneration vs the idempotency fingerprint — bypass mechanism unstated
- **UX anchor:** EXPERIENCE.md § Component Patterns, Generate form: explicit "Regenerate entire lesson…" "re-runs the pipeline, **bypassing the idempotency cache**" (FR-7).
- **Architecture location:** ADR-004 implements idempotency as a unique index on `drafts.request_fingerprint`; taken literally, an explicit regeneration with unchanged topic+guidance collides with its own fingerprint and would be rerouted — the exact opposite of the UX rule. AD-7/AD-17 acknowledge `scope: lesson` regeneration but not the bypass.
- **Fix:** state in ADR-004/005 that explicit Regeneration carries a `regenerate: true` intent that skips the fingerprint check and refreshes the stored fingerprint on completion.

## LOW

### L1. Diagram chat card `lang` — no language field in the diagram API
- **UX anchor:** § Accessibility Floor: "Player content regions **and diagram cards** set `lang` from the … language tag."
- **Architecture location:** block-edon-ai-diagram-api.md response carries no language/locale field; WI-CHAT-1 cannot set `lang` from contract data.
- **Fix:** add `"lang": "en"` to the `served` response shape.

### L2. Transfer-size label data source unspecified
- **UX anchor:** § Capability Tiers ladder: "All size labels state *transfer* (compressed) size."
- **Architecture location:** sizes exist in `manifest.json` (ADR-012) but nothing says how the Player obtains them (script fields vs manifest fetch).
- **Fix:** one line in ADR-006: frozen asset references in the script (or the delivery response) carry `transferSize` from the publish manifest.

### L3. "Your lecturer updated this lesson" — no version-change signal
- **UX anchor:** § State Patterns, Version pinning: returning Student on a different Published Version sees the one-line notice.
- **Architecture location:** mod-edonlesson §2.3 playback-session response has no "previous attempt's version differs" indicator.
- **Fix:** include `last_attempt_version` (or a boolean `version_changed`) in the playback-session `resume` block.

### L4. Live-session autosave retry ("Not saved — retrying") mechanism only stated for relaunch
- **UX anchor:** § State Patterns, "Edit save failed / offline": edits retained locally, retried, never silent.
- **Architecture location:** ADR-009 mentions localStorage preservation only in the relaunch/expiry context; no named retry loop for in-session autosave failures (the quiz path got an explicit outbox; the authoring path didn't).
- **Fix:** one sentence in ADR-004: failed block-patch autosaves are kept in the same localStorage buffer and retried with backoff while the session lives.

### L5. Narration voice-preference cascade not carried
- **UX anchor:** § Capability Tiers ladder rules: voice preference follows the language tag (en-NG → en-GB → any English).
- **Architecture location:** AD-10's `SpeechSynthesisProvider` specifies the 3 s watchdog but not voice selection.
- **Fix:** add the cascade as a `SpeechSynthesisProvider` config default in AD-10.

### L6. Zero-renderable-Blocks rule not restated where AD-10 owns block filtering
- **UX anchor:** § Component Patterns, Player shell: "A script with zero renderable Blocks renders the major-version can't-play state, never an empty Player."
- **Architecture location:** AD-10 defines unknown-type omission but not the all-omitted edge.
- **Fix:** append to AD-10: if filtering leaves zero renderable Blocks, render the defined cannot-play state.

---

## Confirmed landed (spot-checked, no finding)

- **Item 11 (attempt unit) — complete:** attempt = one full Lesson run pinned to one Published Version; consumed only at first Quiz submission; reload re-attaches, never ends the pinned session, never consumes; cross-version "highest attempt" = max `earned/possible` fraction × grademax; per-Lesson counts; completion-summary best-score line (AD-15, ADR-010).
- **Item 16 (Launch Token) — complete:** 120 s single-use fragment-carried JWT; 8 h absolute Authoring Session; T-15 min pre-expiry warning from bootstrap `expires_at`; autosave durability independent of sessions (revisions + localStorage restore); relaunch-into-same-Draft via last-active-draft record + `draft_hint`; all lifetimes config (AD-14, ADR-009, mod-edonlesson §2.2).
- **Item 17 (quiz durability) — complete:** `submission_uuid` idempotency on (attempt, block, uuid); re-score + persist + outbox rows in one transaction **before ack**; "Saving your score…" gated on ack; client localStorage outbox + `sendBeacon`; attempt consumed at most once per Submit (AD-15, ADR-010).
- **Schema addition (item 15):** sanitiser allowlist preserves `<title>`, `<desc>`, `role="img"`, `aria-label`, `aria-labelledby` (AD-13); `altText` populated at `assemble_validate`; diagram API returns `alt_text`/`long_description` (residual scope note = M2).
- **FR-27 extensions:** `diagram_review_completed`, `diagram_invalidated` in the closed taxonomy (AD-7) (eviction semantics = H2).
- **Per-Block progress events:** `job_progress` rows per stage, SSE + poll fallback, coarse-state degradation (AD-17, ADR-003/005); SSE natively motivated in ADR-001.
- **Showcase detection:** feature-based, all-signals-required, missing/undefined ⇒ demote; `saveData` honored; enhancement chunk ≤ 300 kB post-first-paint, outside the core 150 kB budget (AD-11, ADR-006).
- **Tiers ladder hooks:** glTF ≤ 5 MB transfer / posters ≤ 60 kB / diagram SVG ≤ 150 kB in `budgets.json`, CI + pipeline enforced; one-heavy-Block-live; cached re-load free with honest label reappearance; narration 3 s bounded-start → Floor rung; 10 s sim-readiness watchdog → poster; label-legibility check at sanitisation (360 px font-size/viewBox math).
- **Embedding Contract:** in-page IIFE mount, `edon-p-*` namespaced container-scoped styles, no global resets, self-managed height, new-tab launch (fragment token), Moodle-mobile-app browser hand-off (WI-MOD-3).
- **Resume/reload floor:** viewed marks + quiz state + position + pinned version server-persisted, returned in the playback-session `resume` block.
- **Version pinning:** attempt FK pins the version; new attempts get latest; plugin never implements the rule (residual notice signal = L3).
- **Interpolated limit copy:** AD-20 templating; diagram API `message` interpolated platform-side from tenant config.
- **WCAG consequences:** keyboard-operable simulation params as pre-publish check (3) in ADR-007 (A-35 extended, not narrowed); Player `lang` from script tag (AD-20); preview Low-spec toggle forces Floor tier (ADR-006).
- **Budget-pause semantics:** OQ-9 verbatim — intake pause + Authoring bootstrap banner state, diagrams cache-only, replay untouched (AD-8, ADR-013).
