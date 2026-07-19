---
stepsCompleted: [1, 2, 3, 4, 5, 6]
documentsIncluded:
  prd: prds/prd-2027_edon_sim_pro-2026-07-07/prd.md (+ addendum.md)
  architecture: architecture/architecture-2027_edon_sim_pro-2026-07-17/ARCHITECTURE-SPINE.md (+ docs/adr/ADR-001..014, project-context.md §9 extension)
  epics: epics.md
  ux: ux-designs/ux-2027_edon_sim_pro-2026-07-16/DESIGN.md + EXPERIENCE.md
  integrations: docs/integrations/edon-rag-retrieval.md (v1.2), mod-edonlesson-platform-api.md, block-edon-ai-diagram-api.md
mode: fast-path (directive; findings batched for sign-off; no sprint planning)
---

# Implementation Readiness Assessment Report

**Date:** 2026-07-18
**Project:** 2027_edon_sim_pro (e-DON Lesson Studio)

## 1. Document Inventory

| Type | Canonical file(s) | Status |
| --- | --- | --- |
| PRD | `prds/prd-2027_edon_sim_pro-2026-07-07/prd.md` + `addendum.md` | final (signed off; reconcile + adversarial + rubric reviews present) |
| Architecture | `architecture/architecture-2027_edon_sim_pro-2026-07-17/ARCHITECTURE-SPINE.md` + ADR-001..014 (`docs/adr/`) + `project-context.md` §9 extension | final (stakeholder sign-off 2026-07-18, binding) |
| UX | `ux-designs/ux-2027_edon_sim_pro-2026-07-16/DESIGN.md` + `EXPERIENCE.md` (+ 3 key mockups, a11y/low-spec reviews, validation report) | final |
| Epics & Stories | `epics.md` (whole, 10 epics) | current — updated 2026-07-18 (WI-RAG-0 delivery: Story 2.7 unblocked; contract refs bumped to v1.2) |
| Integration contracts | `docs/integrations/edon-rag-retrieval.md` **v1.2** (WI-RAG-0/1 COMPLETE, 404 correction), `mod-edonlesson-platform-api.md`, `block-edon-ai-diagram-api.md` | current |
| Fixtures | `fixtures/edon-rag/` — 3 recorded production responses (edon-rag v2.1.0) | landed 2026-07-18 |

**Duplicates:** none (single canonical version per type).
**Missing:** none required. Product brief + project-context loaded as foundational context.

## 2. PRD Analysis

### Functional Requirements (29 — FR-1…FR-29, globally numbered)

| ID | Requirement (normative core) |
| --- | --- |
| FR-1 | Lesson Script Schema v1.0: metadata (Tenant, course ref, curriculum ref, version, Citations) + ordered Block list of six MVP types (Slide, Narration, Quiz, Diagram, Model3D, Simulation). |
| FR-2 | Forward compatibility: explicit versioning; Players ignore unknown Block types; Published Versions playable forever; defined major-mismatch "cannot play" state. |
| FR-3 | Schema ships as first-class shared package (validators + docs); no Draft persists without passing validation; backend and Player consume the same package. |
| FR-4 | Grounded generation request: topic + course context (Launch-Token-supplied) + optional guidance; retrieval exclusively from the requesting Tenant's Corpus via edon-rag. |
| FR-5 | Multi-stage pipeline produces validated, schema-conforming Lesson Script; non-conforming output fails the job visibly, never a partial Draft. |
| FR-6 | Citations stored per Block (provenance always stored); Teacher review shows full per-Block Citations; Student Player shows Lesson-level "Sources" only; ungrounded generation fails (A-5). |
| FR-7 | Draft persistence + idempotent cached generation; Regeneration is explicit-only and bypasses the idempotency cache. |
| FR-8 | Asynchronous queued generation with progress; per-Block progress (`job_progress`) is required scope (A-8 upgraded, AD-24). |
| FR-9 | Faithful preview via the same Player + same script; fallback/poster states previewable; all six Block types previewable. |
| FR-10 | Block-level editing: text edits (Slide/Narration/Quiz/Model3D annotations), delete, reorder; Block-level Regeneration for Diagram/Model3D/Simulation; Draft discard; creator-owns + Tenant Admin (OQ-13). |
| FR-11 | Explicit, immutable publication; Drafts and Published Versions coexist; republish creates a new version; latest wins for new sessions. |
| FR-12 | Review Gate enforcement: Students can retrieve Published Versions only; sole exception = sanitised on-demand diagrams. |
| FR-13 | Player renders full ordered Block sequence of all six types. |
| FR-14 | Narration behind a swappable provider. **Amended (addendum §5): publish-time neural TTS (`tts` workload) generating static audio assets; text remains primary modality; republish regenerates only changed audio.** |
| FR-15 | Quiz: MC + short-answer; instant client feedback; deterministic normalised short-answer matching vs Teacher-approved lists; server re-scores authoritatively before any writeback. |
| FR-16 | Model3D Blocks from the Curated Model Library only (licence + attribution metadata); orbit/zoom + authored annotations; no generated 3D geometry. |
| FR-17 | Simulation Blocks in sandboxed iframes (no network/storage, strict CSP, postMessage protocol); authored manipulable parameters; automated pre-publish checks block publish on failure. |
| FR-18 | Low-spec performance: per-Block asset budgets, compression, poster fallbacks (incl. no-WebGL), CI budget enforcement. **Amended (addendum §5): Showcase/Full canonical, modern-device posture; Floor tier best-effort; low-spec CI advisory.** |
| FR-19 | Student diagram requests in existing chat (block_edon_ai), Corpus-grounded, identity-stripped, rendered as labelled SVG. |
| FR-20 | Mandatory allowlist Sanitisation of every LLM-derived SVG before storage/render; failures rejected outright. |
| FR-21 | Diagram caching (Tenant-scoped, pre-LLM), per-Student Rate Limits (cache hits exempt), per-Tenant Quotas (default 20/Student/day). |
| FR-22 | Course placement via mod_edonlesson; embedded Player playback in the Moodle page; plugin stays thin. |
| FR-23 | Completion + gradebook writeback (server-authoritative score); retriable failures; OQ-15 lifecycle semantics (completion definition, retakes, highest attempt, version pinning). |
| FR-24 | Tenant-scoped auth between plugin and platform; Student identity attribution correct. |
| FR-25 | Full Tenant isolation of lessons, assets, caches, Quotas, budgets, logs; no cross-Tenant paths outside Operator endpoints. |
| FR-26 | Per-Tenant Operator config: Budget Ceilings, Quotas, Rate Limits, feature flags (≥ Diagram + Simulation, no redeploy); OQ-9 exhaustion semantics; bounded one-job overrun. |
| FR-27 | Structured Events (canonical closed taxonomy incl. 2026-07-18 extensions) + Cost Telemetry on every LLM call; per-Tenant/per-Lesson cost computable from telemetry alone. |
| FR-28 | Diagram accuracy governance: mandatory grounding, visible AI label, Student report → Teacher review queue, telemetry-sampled spot checks. |
| FR-29 | Moodle-initiated Authoring launch only: signed short-lived Launch Token (Tenant, user, role, course ref); no standalone login; no course enumeration. |

**Post-architecture FR amendments (addendum §5, binding):** publish-time TTS (NarrationProvider seam), Live Q&A embedded course-scoped chat (WI-CHAT-4), V2 reserved-extensions record (record-only), device-posture realignment.

### Non-Functional Requirements (9)

- **NFR-1** Generation performance: median init→Draft-ready < 5 min (p90 = 2× median provisional).
- **NFR-2** Playback performance: bundle/asset budgets + poster fallbacks; device posture per addendum §5 realignment (Showcase canonical; Floor best-effort; low-spec CI advisory).
- **NFR-3** Security: SVG sanitisation, simulation sandbox+CSP, tenant isolation, no wildcard CORS, env-only secrets, key rotation day one.
- **NFR-4** Reliability/durability: Published Versions playable forever; replay independent of LLM availability; failed jobs never corrupt existing content.
- **NFR-5** Observability: structured tenant/user-attributed logging; Cost Telemetry as migration instrument.
- **NFR-6** Cost discipline: generate-once as system property; no per-Student-per-session inference beyond diagrams.
- **NFR-7** Legal/licensing: clean-room (no OpenMAIC/AGPL), permissive deps, GPLv3 thin plugin, licence metadata per 3D asset.
- **NFR-8** Localisation-readiness: externalised strings; language tags on Lesson Script text fields; English content at launch.
- **NFR-9** Data protection: identity-stripped LLM requests, pseudonymised telemetry, configurable retention (12 mo default), processor record.

### Additional Requirements & Constraints

- Invariants I-1..I-4 (generate-once, Review Gate, schema-first, tenant isolation) fence all FRs.
- Success metrics SM-1..SM-5 + counter-metrics SM-C1..C3 + OQ-18 adoption metric — all computable from FR-27 events/telemetry.
- All 18 OQs resolved (OQ-5/6/7/18 in later phases); A-1..A-35 approved.
- External dependencies: edon-rag (contract v1.2, WI-RAG-0/1 **delivered**), Moodle 5.x via mod_edonlesson, LLM adapter, 3D asset sources, block_edon_ai (modifiable companion).
- Non-goals (§8) with two superseded entries per addendum §5 errata mechanism (TTS; device floor).

### PRD Completeness Assessment

Complete and unusually rigorous: stable global FR numbering, testable consequences per FR, closed OQ ledger, indexed assumptions, counter-metrics, and an explicit amendment/errata trail. One hygiene note: the amended posture for FR-14/FR-18 and §8 non-goals lives in `addendum.md` §5 rather than the FR body text — internally documented and traceable, but readers of prd.md alone could act on the superseded browser-TTS/device-floor posture (carried into findings as a LOW item).

## 3. Epic Coverage Validation

The epics document carries its own Requirements Inventory (FR-1..29 + AMD-1/2, NFR-1..9, AR-1..32, UX-DR1..23) and an FR Coverage Map. Every map claim was verified against the actual story acceptance criteria (all 62 stories read in full), not taken on assertion.

### FR Coverage Matrix (verified against story ACs)

| FR | Epic/Story coverage (verified) | Status |
| --- | --- | --- |
| FR-1 | 1.1 (schema package: metadata, six Block types, camelCase, AD-2 fields) | ✓ |
| FR-2 | 1.1 (version rules + fixture corpus) + 4.9 (Player plays unknown-block/future-version fixtures) | ✓ |
| FR-3 | 1.1 (js/py validators agree; docs suffice for renderer authors) | ✓ |
| FR-4 | 2.3 (reject missing topic/context), 2.6 (form, no picker), 2.1 (tenant-scoped retrieval) | ✓ |
| FR-5 | 2.2 (config engine, no partial Draft), 2.3 (validate before persist) | ✓ |
| FR-6 | 2.3 (per-Block Citations, ungrounded fails), 3.2 (Teacher panel), 4.7 (Student Sources) | ✓ |
| FR-7 | 2.4 (normalise_key idempotency, no charge), 3.5 (explicit regen bypasses cache) | ✓ |
| FR-8 | 2.5 (transactional enqueue, SSE per-Block progress), 2.6 (progress card) | ✓ |
| FR-9 | 3.6 (real Player, observer mode, Low-spec toggle, Simulation interactive) | ✓ |
| FR-10 | 3.3 (A-28 map), 3.5 (reorder/delete/discard + regen framework), wired 7.2/9.3/10.4 | ✓ |
| FR-11 | 3.7 (DB-immutable versions, If-Match publish, republish → new version) | ✓ |
| FR-12 | 3.7 (no Student path to Drafts), 4.2/4.9 (delivery + not-available state) | ✓ |
| FR-13 | 4.3–4.5 (core types), 7.2 (Diagram), 9.4 (Model3D), 10.5 (Simulation) | ✓ |
| FR-14 | 4.4 (PregeneratedAudio → SpeechSynthesis → transcript chain, 3 s watchdog) | ✓ |
| FR-15 | 4.5 (instant client feedback, deterministic matching), 4.6 (server-authoritative, idempotent) | ✓ |
| FR-16 | 9.1 (ingest + licence rejection), 9.2 (seed intake), 9.3 (selection stage), 9.4 (viewer) | ✓ |
| FR-17 | 10.1 (sandbox+protocol), 10.2 (checks), 10.4 (template stage), 10.5 (frame), 10.6 (freecode) | ✓ |
| FR-18 | 4.1 (budgets CI), 4.8 (tiers/degradation), 9.4/10.5 (posters), 11.2 (perf gates) | ✓ |
| FR-19 | 7.3 (endpoint flow), 8.1 (chat surface) | ✓ |
| FR-20 | 7.1 (single sanitiser gate, a11y-preserving allowlist, legibility check) | ✓ |
| FR-21 | 7.3 (cache-first, zero-cost rows), 7.4 (limits + humane copy) | ✓ |
| FR-22 | 5.3 (picker/session APIs), 6.2 (activity creation), 6.3 (embed) | ✓ |
| FR-23 | 4.6/4.7 (attempts/completion), 5.4 (outbox), 6.4 (scheduled task + gradelib) | ✓ |
| FR-24 | 5.2 (tenant s2s auth, rotation, CORS), 1.4 (pseudonym foundation) | ✓ |
| FR-25 | 1.3 (TenantContext + RLS + isolation test); binds every story DoD | ✓ |
| FR-26 | 1.6 (reserve→settle, OQ-9 verbatim), 1.8 (operator config); UX in 2.6/7.4/8.4 | ✓ |
| FR-27 | 1.7 (closed taxonomy, transactional events); emission per feature; 11.6 (computability) | ✓ |
| FR-28 | 7.3 (verbatim label), 7.5 (report/queue backend), 7.6 (review UI + invalidation), 8.2 (chat label/report) | ✓ |
| FR-29 | 5.1 (verification/sessions), 6.5 (minting), 1.4 (token infra + dev CLI) | ✓ |
| AMD-1 | 3.8 (publish-time TTS, text-hash keying), 4.4 (audio provider) | ✓ |
| AMD-2 | 8.3 (WI-CHAT-4 course-scoped embed) | ✓ |

### Missing Requirements

**None.** No PRD FR lacks a story home. No epic requirement exists that is absent from the PRD/addendum/spine/UX corpus (AMD-1/2 trace to addendum §5; AR-* to the spine; UX-DR* to DESIGN/EXPERIENCE).

### Coverage Statistics

- Total PRD FRs: 29 (+ 2 binding addendum amendments) — **31/31 covered, 100%**
- NFR-1..9: all mapped (verified: NFR homes exist in stories cited by the NFR coverage note)
- AR-1..32: all mapped; AR-30 correctly non-blocking by construction
- UX-DR1..23: all mapped (alignment verified in step 4)

## 4. UX Alignment Assessment

### UX Document Status

**Found and final:** DESIGN.md + EXPERIENCE.md (2026-07-16 run), with a11y/low-spec reviews, validation report, and three key mockups. Full-line verification pass executed (both spines read completely; ~229 normative UX requirement units enumerated, 223 traced to a UX-DR and/or story AC).

### Alignment Results (clean)

- All 23 UX-DRs present in the epics inventory, mapped, and restated accurately in story ACs.
- All 26 EXPERIENCE Component Patterns rows and all 33 State Patterns rows have story homes.
- Device-posture realignment (addendum §5) consistently applied across epics — no epic text treats the low-spec floor as blocking.
- Accessibility floor fully carried (schema fields → Teacher editing → sanitiser preservation → keyboard checks → AA audit).
- UX ↔ architecture: every UX mechanism has an AD home; zero UX requirements lacking an architectural mechanism.
- Values/copy parity: dimensions, budgets, and quoted copy strings in epics match the spines (one exception — F2 below).
- UX validation-report resolutions verified present, except two partials (F9, F1).

### Alignment Issues (carried into §6 findings)

| # | Sev | Issue |
| --- | --- | --- |
| F1 | MED | `curriculumRef` is "Teacher-correctable in review" (AD-2, UX Open Item 12) but no story AC or UX-DR implements the correction surface (Story 3.3 / UX-DR7 omit it). |
| F2 | MED | "Report this diagram" control: ≥ 44 px in UX-DR20/Story 8.2 vs ≥ 48 px Player/chat floor in UX-DR22/Story 11.4 — built to 8.2, it fails the 11.4 audit. Conflict originates inside EXPERIENCE.md (144 vs 217). |
| F3 | MED | EXPERIENCE Simulation-frame component row + Flow 2 narrative still show pre-amendment tap-to-load default; normative sources (tier table, AD-11, Story 10.5) say auto-load default. UX-spine residue only — epics are correct. |
| F4 | LOW | Tenant-Admin banner classed gold-Warning in one EXPERIENCE row vs Info elsewhere; epics sided with Info (consistent with DESIGN's gold reservation) — spine gives no explicit winner. |
| F5 | LOW | DESIGN rows spec 44 px narration/Model3D controls vs the ≥ 48 px Player floor enforced in epics. |
| F6 | LOW | Webfont residue: EXPERIENCE tier table + one DESIGN line still read Showcase-only; normative statements + epics say standard on all capable devices. |
| F7 | LOW | Story 10.4 lacks an AC populating Simulation-poster `altText`/`longDescription` (Diagram 7.2 and Model3D 9.3 both carry it; 11.4 audits it end-to-end). |
| F8 | LOW | DESIGN § Elevation & Depth (two sanctioned shadows; "Player uses no box-shadows") has no UX-DR/story home. |
| F9 | LOW | Validation-report F-5 resolution claims a `user-scalable=yes` integration requirement fixed into the spine — untraceable in any current artifact; surviving mitigation is the View-larger affordance (7.2). |
| F10 | LOW | AMD-1 authoring-side TTS-failure UX unspecified in UX spines; Story 3.8 bridges with a self-flagged `[ASSUMPTION]` awaiting confirmation. |
| F11 | LOW | Terminology drift: "Launch Token expiry" used for the mid-review scenario that is actually Authoring-Session expiry (AD-14); behavior implemented correctly in 5.1. |

### Warnings

None beyond the table — no missing UX documentation, no unsupported UI components.

## 5. Epic Quality Review

### Epic structure — user value & independence

| Epic | User-value framing | Independence | Verdict |
| --- | --- | --- | --- |
| 1 Schema & Foundation | Value-framed ("contract and rails"); greenfield setup early is sanctioned practice; schema-first is a stakeholder directive | Stands alone | ✓ (accepted foundation epic) |
| 2 Grounded Generation | Teacher outcome (cited Draft) | Needs Epic 1 only; fixtures decouple from external WI-RAG-0 (now delivered anyway) | ✓ |
| 3 Review Gate & Publish | Teacher outcome | Needs 1–2 | ✓ |
| 4 Player Core | Student outcome | Needs 1–3; **deliberately does not need Epic 5** — dev-token path (1.4) makes playback testable pre-Moodle, stated in 4.2 | ✓ |
| 5 Platform LMS Edge | Platform-side of Epic 6's user value; borderline-technical framing but correctly sequenced before its consumer | Needs 1–4 (outbox rows from 4.6) | ✓ (minor framing note) |
| 6 mod_edonlesson | Teacher/Student outcome in Moodle | Needs 5 | ✓ |
| 7 Diagram Channel | Teacher + Student outcome | Needs 1–3 (pipeline, regen framework, Course home) | ✓ |
| 8 block_edon_ai | Student outcome | Needs 7 | ✓ |
| 9 Model3D (BLOCKED: OQ-6) | Teacher/Student outcome | Needs 2–4; 9.1 exempted from the OQ-6 block by tagged `[ASSUMPTION]` so tooling precedes curation | ✓ structure; externally blocked as recorded |
| 10 Simulations | Student outcome | Needs 2–4 (3.7 publish checks wiring) | ✓ |
| 11 Showcase & Hardening | Student polish + launch-readiness | Last; consumes everything | ✓ |

No epic requires a later epic. No circular dependencies. Milestone gates are metadata, not stories — correct.

### Dependency analysis (story level)

- Within-epic ordering is backward-only with **one exception (Q1 below)**: Story 3.7's publish-job AC names "TTS stage (Story 3.8)" in its stage sequence — a forward reference to the next story.
- Entity-creation timing is exemplary: tables land when first needed (tenants 1.3; drafts 2.4; attempts+outbox 4.6; review queue 7.5; MODEL_ASSET 9.1; SIM_TEMPLATE 10.3). No create-everything-upfront story exists.
- No starter template (AR-31); scaffold is 1.2 with a minimal bootstrap folded into 1.1 (tagged assumption) per the schema-first stakeholder directive — acceptable deviation, noted.
- External dependencies are explicit and correctly marked: 9.2 (EXTERNAL INPUT — stakeholder-curated seed, blocks M5), 6.3 (staging Moodle w/ production theme, M3 gate item). Story 2.7's former external block is resolved (WI-RAG-0 delivered).

### Story quality findings

| # | Sev | Finding | Remediation |
| --- | --- | --- | --- |
| Q1 | MED | **Forward dependency 3.7 → 3.8:** the publish pipeline AC includes the TTS stage delivered by the *next* story, so 3.7 as written cannot complete first. | Either swap 3.7/3.8 order, or add to 3.7: "TTS stage is a no-op passthrough until 3.8 lands." One-line fix. |
| Q2 | MED | **Fixture-shape test vs real fixtures:** Story 2.1's AC fails any fixture departing from the contract shape, but the committed production fixtures carry an extra per-chunk `metadata` object (`indexed_at`) not in the v1.2 contract. A strict shape test fails the real fixtures on day one. | Decide: document `metadata` as an allowed additive field in v1.2 (recommended — forward-compatible consumer posture), or specify the shape test as unknown-field-tolerant in 2.1's AC. |
| Q3 | LOW | **Block-Regeneration framework (3.5) has no regenerable Block type until Epic 7** (A-28 excludes Slide/Quiz/Narration): the framework's end-to-end AC is only fully exercisable against a stub stage at Epic 3 time. | Add to 3.5: "verified against a stub regenerable stage; first real consumer is 7.2." |
| Q4 | LOW | **Chunky stories:** 1.2 (scaffold+CI+deploy skeleton+two decisions) and 4.6 (attempts+scoring+idempotency+submission UI) are each near epic-slice size; both remain coherent single-PR-able units with testable ACs. | Optional split at sprint planning (1.2 → scaffold/CI vs deploy skeleton; 4.6 → server model vs submission UX); no artifact change required. |
| Q5 | LOW | **Epic 5 framing** is platform/technical ("speaks its integration surface"); acceptable because its user value lands in Epic 6 and sequencing is correct. | None required; optionally reword the epic goal to name the Teacher/Student outcome it enables. |

### AC quality

Given/When/Then structure throughout; ACs are specific, testable, and consistently cite their governing FR/AD/UX-DR — traceability is the best I have reviewed. Error paths are first-class (dedicated edge-state story 4.9; failure ACs in 2.3/2.5/3.4/3.8/4.4/4.6/7.1/10.5). Every story inherits the project-context §7 DoD. No vague ACs found.

### Open `[ASSUMPTION]` tags requiring batch confirmation (12)

1.1 minimal-bootstrap-in-schema-story · 1.2 GitHub Actions default · 1.7 taxonomy-enum enforcement of "closed" · 2.6 dev-token launch as sanctioned entry · 3.8 TTS failure ⇒ publish-without-audio (self-flagged for confirmation; = UX F10) · 6.1 Moodle privacy/backup APIs folded in · 8.3 chat gracefully absent, never a hard dependency · 9.1 platform-global model library with tenant visibility rules · Epic 9 preamble: OQ-6 block gates 9.2–9.4, not 9.1 tooling · 10.3 template seed count/coverage set at story kickoff (no numeric bar) · 10.6 `feature.simulation_freecode` flag name · 11.5 alert transport chosen in-story.

## 6. Summary and Recommendations

### Overall Readiness Status

**READY** — with a short list of pre-sprint artifact corrections, none architectural.

Traceability is complete (31/31 FRs + all NFR/AR/UX-DR inventories verified against story ACs), epic structure is sound (no technical-milestone epics, no inter-epic forward dependencies, exemplary entity-creation timing), and the two external dependencies are correctly isolated: WI-RAG-0/1 **delivered** (edon-rag v2.1.0; Story 2.7 unblocked; fixtures corroborate the contract), and **OQ-6 remains open** — Epic 9 stays blocked, stakeholder-owned, correctly fenced so it blocks only 9.2–9.4 and the M5 gate.

### Findings register (21 total: 0 critical, 0 high, 7 medium, 14 low)

**Medium (fix before or at sprint-planning time — all are small edits):**
1. **Q1** Forward dependency: Story 3.7's publish AC names the 3.8 TTS stage — reorder or add a stub-until-3.8 line.
2. **Q2** Story 2.1's strict fixture-shape test fails the real fixtures (undocumented additive `metadata.indexed_at` per chunk) — document the field as additive in v1.2 (recommended) or make the test unknown-field-tolerant.
3. **F1** `curriculumRef` "Teacher-correctable in review" (AD-2/UX item 12) has no correction-surface AC — add to Story 3.3 + UX-DR7.
4. **F2** 44 px vs 48 px conflict on the chat report control (8.2 vs 11.4; originates in EXPERIENCE.md) — pick 48 px (recommended: satisfies both).
5. **F3** EXPERIENCE Simulation-frame row + Flow 2 still narrate pre-amendment tap-to-load default (epics are correct) — UX-spine residue fix.
6. **D1** Stale "WI-RAG-0 does not exist in production" text survives in **signed-off** artifacts: ARCHITECTURE-SPINE.md:345, ADR-005:12, project-context.md §9 (edon-rag bullet), plus a v1.1 pointer at block-edon-ai-diagram-api.md:19 — needs authorization to edit signed-off docs.
7. **D2** `chunk_id`/`document_id` stability across re-indexing is contractually required (I-3 citations) but unverifiable from fixtures (ids look like row ids: "8", "9"…) — confirm the v2.1.0 stability guarantee with the edon-rag stream. Mitigation already in place: AD-2's citation required-set + platform-stored excerpts mean replay never depends on id dereference.

**Low (14):** F4 banner class (epics chose Info — ratify), F5 44 px DESIGN rows, F6 webfont Showcase-row residue, F7 Story 10.4 missing Simulation-poster altText AC, F8 elevation/shadow rules homeless, F9 `user-scalable` claimed-fix untraceable, F10 TTS-failure UX unspecified (= 3.8 assumption), F11 "Launch Token expiry" naming drift, Q3 regen framework stub-verified until Epic 7, Q4 chunky stories 1.2/4.6 (optional split), Q5 Epic 5 framing, D3 observed `document_ids` filter beyond contract (adopt or ignore), D4 WI-RAG-3 completion asserted via DoD — verify typed models at 2.7's staging smoke, D5 PRD body text (FR-14/FR-18/§8) superseded only via addendum §5 — hygiene note for prd.md readers.

### Recommended Next Steps

1. Obtain sign-off on the decision list (§7 of the sign-off package) — the 7 medium fixes are collectively < 20 lines of artifact edits.
2. Apply authorized fixes (epics.md one-liners; UX-spine residue; signed-off-doc deltas if authorized).
3. Send two questions to the edon-rag stream: chunk-id stability guarantee (D2); `document_ids` filter — contract or ignore (D3).
4. Then run sprint planning (deliberately **not** started per directive). Epic 9 stories stay out of any sprint until the stakeholder's OQ-6 seed library lands; 9.1 (ingest tooling) is the sanctioned exception.

### Final Note

This assessment identified 21 issues across coverage, UX-alignment, story-quality, and integration-currency categories — none critical or high. The planning corpus is implementation-ready once the medium items are dispatched; nothing found challenges the architecture, the invariants, or the epic decomposition.

**Assessed:** 2026-07-18 · Fast-path directive run · PRD/UX/Architecture/epics all final or current · WI-RAG-0/1 delivery verified against committed production fixtures.

## 7. Sign-off Record & Application Log (2026-07-18, john)

**All findings signed off; fixes applied same day. Sprint planning explicitly not started.**

### Decisions (medium findings)

| # | Decision | Applied |
| --- | --- | --- |
| 1 (Q1) | TTS stage is a no-op passthrough until 3.8; no story swap | ✅ epics.md Story 3.7 AC |
| 2 (Q2) | v1.2 allows additive `metadata` keys; shape tests strict on required set, tolerant of additive metadata | ✅ contract §3 response table + epics.md Story 2.1 AC |
| 3 (F1) | `curriculumRef` Teacher-correctable in review per AD-2 | ✅ epics.md Story 3.3 AC + UX-DR7 |
| 4 (F2) | 48 px for the chat report control | ✅ EXPERIENCE.md:144 (origin), DESIGN.md chat row, epics.md UX-DR20 + Story 8.2 |
| 5 (F3) | Fix UX-spine tap-to-load residue | ✅ EXPERIENCE.md Simulation-frame row + Flow 2 steps 3–4 (data-saver premise) |
| 6 (D1) | Status-only delivery deltas to signed-off docs | ✅ ARCHITECTURE-SPINE.md (M1 line), ADR-005, project-context.md §9, block-edon-ai-diagram-api.md (v1.2 pointer) — no rule changes |
| 7 (D2) | chunk_ids are DB row ids; may change on delete+re-upload; accepted — citation integrity via stored excerpt + document_title (AD-2) | ✅ contract §3 field-table stability note |

### Open questions resolved

- `document_ids` filter **adopted** into contract v1.2 as a supported optional filter (implemented + tested edon-rag-side; not a platform dependency). ✅ contract §3 request table.
- **OQ-6 stays open; Epic 9 stays blocked; 9.1 excepted.** No change.

### Assumptions

All 12 standing `[ASSUMPTION]` tags in epics.md **confirmed** (recorded in the Epic List preamble), plus the WI-RAG-3-via-DoD tag — WI-RAG-3 marked confirmed in contract v1.2; platform-side verification lands at Story 2.7's staging smoke. Contract v1.2 status is now **final (signed off)**.

### Low findings — application

**Applied (pure text corrections):** F3 (with decision 5), F4 Tenant-Admin banner ratified Info (EXPERIENCE.md), F5 DESIGN 44→48 px narration/Model3D rows, F6 webfont Showcase-row/naming residue (EXPERIENCE tier table + DESIGN Player shell), F7 Story 10.4 poster `altText` AC, F8 elevation rules homed in UX-DR1, F11 "Authoring Session expiry" naming (epics UX-DR8 + Story 3.4; EXPERIENCE session-ending row, Block-editor durability rule, Flow 1), Q3 stub-verification note in Story 3.5, D5 PRD supersession pointers (FR-14, FR-18, §8 TTS non-goal).

**Left itemized for the dev loop (not pure text):** F9 (`user-scalable` claimed fix untraceable — needs a rule decision), F10 (TTS-failure UX row — assumption confirmed; a designed State Patterns row can land with Story 3.8), Q4 (optional story splits at sprint planning), Q5 (Epic 5 framing — cosmetic), D4 (WI-RAG-3 verification at 2.7's smoke — now tracked in the contract itself).
