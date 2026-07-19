---
stepsCompleted: [1, 2, 3]
inputDocuments:
  - _bmad-output/planning-artifacts/prds/prd-2027_edon_sim_pro-2026-07-07/prd.md
  - _bmad-output/planning-artifacts/prds/prd-2027_edon_sim_pro-2026-07-07/addendum.md
  - _bmad-output/planning-artifacts/architecture/architecture-2027_edon_sim_pro-2026-07-17/ARCHITECTURE-SPINE.md
  - _bmad-output/planning-artifacts/ux-designs/ux-2027_edon_sim_pro-2026-07-16/DESIGN.md
  - _bmad-output/planning-artifacts/ux-designs/ux-2027_edon_sim_pro-2026-07-16/EXPERIENCE.md
  - _bmad-output/project-context.md
---

# 2027_edon_sim_pro — Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for e-DON Lesson Studio, decomposing the requirements from the PRD (final, 2026-07-18), the PRD addendum (incl. §5 post-architecture stakeholder amendments), the Architecture Spine (AD-1..AD-24, final), the UX spine pair (DESIGN.md + EXPERIENCE.md, final), and the binding project-context.md into implementable stories. Epic sequencing follows the M1–M6 milestone gates (spine § Release & milestones).

## Requirements Inventory

### Functional Requirements

FR-1: Lesson Script Schema v1.0 (`"schema": "1.0"`) covering lesson metadata (Tenant, course reference, curriculum reference, version, Citations) and an ordered Block list with the six MVP Block types (Slide, Narration, Quiz, Diagram, Model3D, Simulation).
FR-2: Forward compatibility — explicit versioning; Players ignore unknown Block types gracefully; Published Versions playable forever; defined minor/major version-mismatch behavior (can't-play state, never silent corruption); enforced by CI fixtures with unknown Block types and future version stamps.
FR-3: Schema ships with validators and documentation as a first-class package consumed by backend and Player alike; no Lesson Script persists as a Draft without passing validation.
FR-4: Grounded generation request — Teacher initiates a Generation Job with topic + Course Context (from Launch Token only) + optional guidance; retrieval exclusively from the requesting Tenant's Corpus via edon-rag; no prompt-engineering skill required.
FR-5: Schema-conforming multi-stage pipeline (lesson plan → per-Block content → validation); a non-conforming run fails the job visibly; never a partial or invalid Draft.
FR-6: Citations stored per-Block (provenance always stored); Teacher review shows full per-Block Citations; Student Player shows Lesson-level "Sources" only; ungrounded generation fails the job (A-5); edits preserve Citations as provenance-of-generation.
FR-7: Draft persistence, idempotency cache on a normalised request key (identical request returns existing Draft, no LLM call), Regeneration always an explicit Teacher action that bypasses the idempotency cache.
FR-8: Asynchronous Generation Jobs with progress feedback (queued/in progress/complete/failed minimum; per-Block `job_progress` required per A-8 upgrade/AD-24); failed jobs present a Teacher-readable reason and leave no Student-visible artifact.
FR-9: Faithful preview — same Player, same script as Students; poster/fallback states previewable (A-27); all six Block types previewable including Simulation interaction.
FR-10: Block-level editing per the A-28 editability map — text edits (Slide, Narration, Quiz incl. answers/feedback, Model3D annotations), Block deletion, reordering; Block-level Regeneration for Diagram/Model3D/Simulation; Draft discard with Structured Event; creator-owns model with Tenant Admin override (OQ-13); every edit revalidates.
FR-11: Explicit, immutable publication; Drafts and Published Versions coexist; republish creates a new Published Version; prior versions remain playable; new sessions get latest.
FR-12: Review Gate enforcement — Student surfaces retrieve Published Versions only; sole exception: sanitised on-demand Diagram Requests; unpublished access yields a clear "not available" outcome.
FR-13: Player renders a Published Version's full ordered Block sequence (all six Block types) in script order.
FR-14: Narration behind a swappable provider — pre-generated audio primary when present (see AMD-1), browser SpeechSynthesis fallback, graceful degradation to always-accessible narration text (A-9).
FR-15: Quiz Blocks (multiple-choice + short-answer) — instant client-side feedback; deterministic normalised short-answer matching against Teacher-approved accepted-answer lists (OQ-4); server re-scores every submission authoritatively before any gradebook writeback.
FR-16: Model3D Blocks render Curated Model Library glTF assets (licence + attribution metadata mandatory) in an interactive orbit/zoom viewer with authored annotations; generation selects and configures — never creates geometry.
FR-17: Simulation Blocks in sandboxed iframes (no network, no storage, strict CSP, postMessage protocol only) with authored manipulable parameters; automated pre-publish checks (load clean, protocol honored, params present + keyboard-operable, resource budget) block publish on failure with a per-Block readable reason (A-11/A-35).
FR-18: Low-spec performance — per-Block asset size budgets, compression, poster-image fallback as a required first-class path (incl. no-WebGL); lesson fully completable in degraded states; CI budget enforcement. (Device posture per addendum §5: Showcase canonical, Floor best-effort, low-spec CI advisory.)
FR-19: Grounded Student Diagram Requests in the existing block_edon_ai chat — Tenant-scoped retrieval, grounding mandatory in the prompt, identity-stripped before the adapter call, rendered as labelled SVG in chat.
FR-20: Mandatory allowlist Sanitisation of every LLM-derived SVG (direct or via intermediate representation, both sides) before storage or rendering; failures reject outright with a clear outcome + Structured Event.
FR-21: Diagram caching Tenant-scoped on a normalised key before any LLM call; per-Student Rate Limits (cache hits exempt); per-Tenant Quotas (default 20/Student/day, tunable); cache hits/misses in Cost Telemetry.
FR-22: Course placement of Published Versions via mod_edonlesson; Player embeds in the Moodle page (no redirect); the plugin stays thin with no proprietary logic.
FR-23: Completion and gradebook writeback via Moodle APIs — server-authoritative scores only; completion = all declared Blocks viewed + all Quiz Blocks submitted; retakes with Teacher-configurable attempt limits; highest attempt recorded; version pinning per attempt; retriable writeback with Structured Events (24 h eventual-consistency window, A-25).
FR-24: Tenant-scoped authentication between mod_edonlesson and the platform; Student identity passes through for correct attribution.
FR-25: Full Tenant isolation of lessons, assets, caches, Quotas, Budget Ceilings, and logs; no cross-Tenant path outside explicit Operator-role endpoints.
FR-26: Per-Tenant Operator configuration — Budget Ceilings, generation/diagram Quotas, per-user Rate Limits (platform defaults, Tenant-overridable), feature flags (at minimum Diagram feature + Simulation Blocks, no redeploy); enforcement at platform layer; OQ-9 exhaustion semantics (pause with notice, cache-only diagrams, replay never blocked, bounded one-job overrun).
FR-27: Structured Events (closed canonical taxonomy incl. the five architecture-ratified extensions) and Cost Telemetry on every LLM call (fixed field contract); all SMs computable from stored data alone; diagram cache hits emit zero-cost rows; pseudonymised Student identifiers.
FR-28: Diagram accuracy governance — verbatim "AI-generated — verify against your course materials" label, Student report control feeding a Teacher review queue, telemetry-sampled spot checks.
FR-29: Moodle-initiated Authoring launch only — signed short-lived single-use Launch Token (Tenant, user, role, course reference) minted by mod_edonlesson; expired/tampered tokens land on a clear relaunch notice; the platform never enumerates Moodle courses.
AMD-1 (addendum §5, binding): Voiced AI Lessons — publish-time neural TTS via the `tts` workload behind the NarrationProvider seam; audio stored as static lesson assets (per-lesson cost, zero per-student); republish regenerates only changed audio (per-Block text hash); text always the primary modality.
AMD-2 (addendum §5, binding): Live Q&A — the existing block_edon_ai chat, course-scoped, presented with the lesson activity page (WI-CHAT-4); no new inference economics; NFR-9 unchanged.

### NonFunctional Requirements

NFR-1: Generation performance — median initiation→"Draft ready" under 5 minutes (queue time included); p90 tracked at 2× the median bar (A-34).
NFR-2: Playback performance — usable on low-spec Android hardware; budgets + poster fallbacks; per addendum §5 the blocking perceived-performance check runs on a standard modern profile (title + first Slide text ≤ 2.5 s), the throttled low-spec CI profile is advisory.
NFR-3: Security — allowlist SVG Sanitisation; Simulation sandbox with strict CSP; Tenant isolation everywhere; no wildcard CORS (per-Tenant origins); secrets via env only; API key rotation without downtime.
NFR-4: Reliability/durability — Published Versions playable forever; replay independent of LLM provider availability; failed jobs never corrupt Drafts or Published Versions.
NFR-5: Observability — structured Tenant- and user-attributed logging; Cost Telemetry as the model-migration instrument.
NFR-6: Cost discipline — generate-once as a system property; no per-Student-per-session inference beyond Diagram Requests.
NFR-7: Legal/licensing — clean-room (no OpenMAIC/copyleft code); permissive platform dependencies (CI licence gate); mod_edonlesson GPLv3 and thin; licence + attribution metadata on every curated 3D asset.
NFR-8: Localisation-readiness — no hardcoded user-facing strings (externalised, CI-linted per AD-20); Lesson Script text fields carry a language tag.
NFR-9: Data protection — no Student personal identifiers to external LLM providers; pseudonymised telemetry (per-tenant HMAC); configurable log retention (default 12 months); maintained processor record.

### Additional Requirements

**Architecture invariants binding all stories (spine AD-1..AD-24 — the full rule text in ARCHITECTURE-SPINE.md governs; keyed here for coverage):**

- AR-1 (AD-1): One backend deployable + workers; framework-free `core`; thin routers/tasks; import-linter CI contract.
- AR-2 (AD-2): `/schema` JSON Schema 2020-12 as the only content contract; MAJOR.MINOR rules; reserved-extensions list recorded; `audioRef`, `curriculumRef {value, source}`, `altText`/`longDescription`, citation required-fields set (`sourceChunkId`, `documentTitle`, `excerpt`), `transferSize` on heavy-asset refs; Pydantic mirrors proven equivalent in CI against the shared fixture corpus (incl. unknown-block + future-version fixtures); js + py validator wrappers.
- AR-3 (AD-3): Single async LLM adapter, workload-keyed (`lesson_generation`, `simulation_generation`, `diagram_generation`, `tts`); exactly two drivers (`openai-compatible`, `anthropic-native`); identity-free request types with mandatory `governance_ref`; chat + speech surfaces; telemetry + governance in the call path.
- AR-4 (AD-4): Procrastinate 3.x on platform PostgreSQL; transactional enqueue for loss-intolerant jobs; queues `generation`/`delivery`/`maintenance`; `JobPort` in core.
- AR-5 (AD-5): PostgreSQL system of record; validated JSONB scripts; `published_versions` immutable at the DB (no UPDATE/DELETE grants); one mutable Draft per Lesson with monotonic `revision` (If-Match, 409); publish as a progress-visible job: revalidate → checks → TTS for changed Narration Blocks → asset freeze → single final transaction.
- AR-6 (AD-6): `TenantContext` required for all data access; PostgreSQL RLS on every tenant-owned table (migration CI gate); operator access only via separate audited router + DB role.
- AR-7 (AD-7): All writes through core use-cases; Structured Events inserted in the same transaction as state; closed event taxonomy.
- AR-8 (AD-8): One governance subsystem (quotas/rate limits/budgets over one `action_type` vocabulary), reserve→settle in the adapter path + pre-enqueue check with machine codes; `governance_state` in bootstrap responses; cache hits never charge; default per-tenant generation concurrency 1.
- AR-9 (AD-9): `StorageDriver` port (launch: VPS filesystem + nginx X-Accel-Redirect); tenant-scoped key prefixes; `asset://` stable ids; publish freeze into immutable `v{n}/` prefix with manifest; machine-safe keys.
- AR-10 (AD-10): Player composition — `BlockRegistry`, `LessonDeliverySource` (async block-iterator signature), `NarrationProvider` (two MVP providers: PregeneratedAudio + SpeechSynthesis fallback with 3 s watchdog), `ResultsSink` (no-op in preview); no runtime schema validation in the Player.
- AR-11 (AD-11): Self-contained IIFE `EdonPlayer.mount`; ES2017/`chrome61` floor; namespaced `edon-p-*` styles; Showcase-canonical device posture (auto-load default, tap-to-load only under data-saver signals, webfonts standard post-first-paint); all budgets in one CI-enforced `budgets.json` (launch values per spine: core ≤ 180 kB gzip hard fail; model3d ≤ 250 kB; simulation ≤ 60 kB; fonts+motion ≤ 300 kB; glTF ≤ 10 MB hard/6 MB preferred; posters ≤ 100 kB; SVG ≤ 200 kB; audio ≤ 800 kB/Block, ≤ 10 MB/lesson); at most one heavy Block live.
- AR-12 (AD-12): Simulation sandbox law — `sandbox="allow-scripts"`, srcdoc CSP `default-src 'none'`, postMessage protocol v1 (pinned message set, param descriptor array, `data-edon-param` markers), 10 s readiness watchdog → poster; dual mode `template|freecode` in schema (template = launch default per OQ-5; freecode behind tenant flag only after the ADR-002 ≥ 70% gate); headless pre-publish checks incl. keyboard operability.
- AR-13 (AD-13): One server-side allowlist sanitiser (defusedxml) as the only path to storage; preserves `<title>`, `<desc>`, `role="img"`, `aria-label`, `aria-labelledby`; runs the diagram label-legibility check (360 px math); client DOMPurify as defense-in-depth only.
- AR-14 (AD-14): Exactly five credential kinds (tenant API keys dual-valid hashed; Launch Tokens HS256 120 s single-use `jti`; Authoring Sessions 8 h HttpOnly; Playback tokens opaque 24 h; Operator keys CLI-issued audited); dev-only token-minting CLI on the same JWT path (pre-Moodle testability); `user_pseudonym = HMAC-SHA256(per-tenant salt, lms_user_id)`; lifetimes are config.
- AR-15 (AD-15): Attempt = one Lesson run pinned to one Published Version, scoped `(lesson_id, activity_ref)`, consumed at first quiz submission; player-declared rendered set is the completion denominator; scores as fractions; exactly one scored submission per (attempt, block), idempotent by client UUID; re-score + persist + outbox in one transaction before ack; observer sessions never write.
- AR-16 (AD-16): LMS-agnostic platform API; grade/completion delivery via pull + ack-with-status outbox drained by the plugin's scheduled task; `writeback_failure`/`writeback_retry`/`writeback_overdue` events; versioned integration contracts in /docs/integrations, changes only via work items.
- AR-17 (AD-17): Pipeline as config (`pipeline.yaml` + prompt files, language-keyed, stable-prefix-ordered); retrieval below score floor fails `ungrounded`; one repair retry per stage then whole-job failure; per-stage `job_progress` rows; atomic per-Block Regeneration; posters derived deterministically from content (never an image model); one `normalise_key` function shared by idempotency + diagram cache (CI asserts no second implementation).
- AR-18 (AD-18): Config over constants for every policy value; tenant flags evaluated at intake + bootstrap; flags never alter delivered script content (Player degrades presentation; server-side Block stripping forbidden); `.env.example` current per story DoD.
- AR-19 (AD-19): Structured JSON logs with bound tenant + pseudonym; fixed unit-tested Cost Telemetry row contract; zero-cost cache-hit rows; SM-1..SM-5 + counter-metrics computable from stored data; retention via nightly maintenance job from `retention.yaml`.
- AR-20 (AD-20): i18n — every user-facing string externalised under `surface.component.slug` keys, CI lint gate; limit copy templated from tenant config; chat/diagram API returns rendered `message` strings, first-party UIs resolve `code + params` client-side.
- AR-21 (AD-21): Diagram channel flow fixed (normalise → cache → governance → identity-stripped retrieval + mini-tier structured generation → sanitise → store + label); pinned review-queue row shape; "Mark reviewed" clears; "Mark invalid" clears + evicts cache (`diagram_invalidated`); humane copy on every non-served outcome.
- AR-22 (AD-22): Playback bootstrap contract — `EdonPlayer.mount(el, {scriptUrl, token, locale})`; first act `GET /api/v1/playback/bootstrap` returning pinned script URL, attempt ids, resume shape, feature flags, governance state, observer, tier hints.
- AR-23 (AD-23): Draft concurrency law — stable plan-minted Block ids; Regeneration participates in the revision sequence; normative 409 recovery (three-way per-Block rebase); token-expiry restores stage as per-Block proposals; publish If-Match with revision-pinned checks; two-writer scenarios are mandatory test-floor cases.
- AR-24 (AD-24): Progress-stream contract — `job_progress` row shape, SSE snapshot-then-tail, named events, `display_key` via language catalog; degradation to coarse states, never a broken stream.

**Toolchain, CI, and repo rules (spine Conventions + project-context build rules):**

- AR-25: One toolchain — pytest + ruff; Vitest + ESLint + Prettier; Playwright (E2E + profiles); no-TypeScript CI lint gate on `/player`, `/authoring`, `/schema/js`; `uv` with committed lockfile; npm workspaces; licence-audit CI gate on both lockfiles; Alembic reversible migrations with RLS-per-table CI check; conventional commits; import-linter contract.
- AR-26: Deployment — Linux VPS, nginx + TLS, systemd units per spine deployment diagram; staging with synthetic tenants + one live smoke tenant; backups (pg_dump + asset rsync off-VPS); CI provider + deploy transport decided at first epic (deferred-decision register).
- AR-27: External integration contracts as versioned docs — edon-rag retrieval v1.2 (course-scoped `POST /api/courses/{moodle_course_id}/retrieve`, `x-api-key`); **WI-RAG-0 DELIVERED 2026-07-18 (edon-rag v2.1.0, 45 tests): the retrieval endpoint is live in production; recorded fixtures committed at `fixtures/edon-rag/`; WI-RAG-1 closed at full strength (locator populated for existing corpora); non-owned course returns 404 (contract v1.2); the live-retrieval slice (Story 2.7) is unblocked**; mod-edonlesson platform API; block-edon-ai diagram API.
- AR-28: Release shape — single full-MVP release through milestone gates M1–M6, each ending in a private pilot-college preview; launch = sponsored pilot ≤ 5 colleges; weekly ops checklist runbook is an in-scope deliverable.
- AR-29: Content deliverables — Curated Model Library ingest pipeline (gltf-transform, Draco, licence metadata mandatory) with the **OQ-6 seed bar: ≥ 20 models across 2–3 NCE science subjects, stakeholder-curated, blocking M5 Model3D stories**; Simulation template seed set as a first-class deliverable.
- AR-30: **ADR-002 launch-model benchmark is a standing stakeholder-owned process** run through the production adapter with zero code changes per candidate; winners land as config. It must not block any epic (per-workload config defaults suffice for development).
- AR-31: No starter template — greenfield monorepo scaffold per the spine source tree (`schema/`, `backend/`, `player/`, `authoring/`, `docs/`), plus companion repos `mod_edonlesson` (GPLv3) and `block_edon_ai` (existing, enhanced).
- AR-32: Operator surface is minimal internal tooling (A-2): CLI + `/operator/*` endpoints for tenant provisioning, credentials, budgets/quotas/flags; audited; no Teacher/Student surface.

### UX Design Requirements

UX-DR1: Implement the DESIGN.md token system (colors, typography ramp, spacing, radii, component tokens) for Authoring UI and Player chrome; enforce the green=settled / gold=AI-awaiting-judgment split (gold never decorative, never text/hairline on light surfaces, always paired with accent-ink); light mode only; error red never used for AI-attention states; elevation per DESIGN.md § Elevation & Depth — two sanctioned authoring shadows, the Player uses no box-shadows.
UX-DR2: Typography per DESIGN.md — Plus Jakarta Sans + Inter (both OFL, licence-gate verified) always in Authoring; Player core bundle webfont-free (system stack first paint) with the standard lazy fonts chunk (Inter + Plus Jakarta Sans) post-first-paint, never render-blocking, never in the core budget; ≥ 14 px meaning-bearing text; caption reserved for metadata.
UX-DR3: Authoring shell components per spec: Button set (labeled actions only, destructive-confirm-only rule), Status chip (Draft/Published/Edited/Needs review/Check failed with defined lifecycle), Lesson card (version history line), Notice banner (info/warning/error; persistent budget-pause banner programmatically associated with the disabled Generate form), branded Empty state pattern, Regenerate control (the only gold control; confirm; "Regenerating…" label swap as state signal).
UX-DR4: Generate form — Topic (required) + Guidance (optional) only, 640 px column, Course Context as read-only locked chip from the Launch Token; inline rejection without topic; idempotent-resubmit reroute to the existing Draft with announced info banner + focus move; the same form serves whole-Lesson Regeneration (prefilled, editable, confirm names Block count, bypasses idempotency).
UX-DR5: Generation progress card — the block-by-block assembly showpiece (glyph + title skeleton → filled row) driven by `job_progress` SSE; degrades to the plain coarse-state card when events are absent; elapsed time; leave-safe copy (never promise a hard number); failure state with readable reason + explicit "Try again".
UX-DR6: Review Workspace — three-pane layout (rail ~280 px / fluid editor / citations ~320 px) with responsive collapse (768–1023: citations sheet; < 768: horizontal block strip); Block rail as a single tab stop with arrow traversal, drag + always-visible-on-focus keyboard reorder buttons, session-local unseen dot (gold fill in accent-ink ring) exposed programmatically; landmarks + skip-to-editor link.
UX-DR7: Block editor per the A-28 editability map — text fields for Slide/Narration/Quiz (questions, answers, accepted-answer lists, feedback)/Model3D annotations; Diagram SVG and Simulation code read-only in a subtle inset with Regenerate adjacent; inline field-pinned validation errors; `altText`/`longDescription` editable as plain text for Diagram Blocks and Model3D/Simulation posters; lesson-level `curriculumRef` Teacher-correctable (`source` flips to `"teacher"`, AD-2).
UX-DR8: Autosave durability — automatic save on valid input with visible "Saved" / "Not saved — retrying" states; no acknowledged edit ever lost to Authoring Session expiry (local preservation + restore into the same Draft as per-Block keep-mine/keep-server proposals when the server moved; relaunch is via a fresh Launch Token, AD-14); session-ending warning banner; Relaunch notice as a one-sentence dead end.
UX-DR9: Citations panel — per-Block collapsible citation cards (excerpt → Grounding Chunk metadata); deleting a Block visibly drops its Citations.
UX-DR10: Preview overlay — the real Player against the current Draft; device-width toggle (Phone 360 / Tablet 768 / Full) + Low-spec view toggle (Floor-tier states, primary-wash selected treatment, honesty helper text); Esc/Close returns with editor state intact; Simulation interactive in preview.
UX-DR11: Publish dialog — visible pre-publish check rows (pass/fail + per-Block readable reason); blocked state keeps failures visible with Regenerate-or-delete exits; success confirm names the version number and points to Moodle placement.
UX-DR12: Course home — own Drafts + Tenant Published Versions as Lesson cards; College library tab (Tenant-wide Published Versions, "Duplicate as my draft"); Tenant Admin persistent info banner naming the owner; branded empty states; Diagram review queue badge in header nav.
UX-DR13: Diagram review queue — thumbnail/request-text/report-count rows; "Mark reviewed" clears; "Mark invalid" (confirm) clears + evicts the Tenant cache entry; both emit Structured Events; empty state.
UX-DR14: Player shell — "Block n of N" progress header with programmatic text equivalent; Back/Next as the only navigation, always available (read-ahead allowed); focus moves to the new Block's heading with live-region announcement; completion summary (tick list, score status, attempts line with "—" fallback, jump-back links, cross-version "best score" line); collapsed Sources section; version-pinning copy ("Your lecturer updated this lesson."); defined can't-play and script-load-failure states; resume restoration visible, never a silent restart.
UX-DR15: Player block components per spec — Slide (instant text, viewed on render); Narration control (explicit play/pause, never autoplays, audio primary → SpeechSynthesis fallback → transcript-by-default Floor state, bounded-start watchdog conversion, "Show text" with AT state, per-Block reset); Quiz (instant per-question feedback with `role="status"`, single-fire Submit, durable-ack "Saving your score…" gating, retry copy, attempts visible, answers-on-client accepted per A-21); Diagram (container-scaled SVG, "View larger" as link, text alternative, no AI label); Model3D viewer (poster first paint, orbit/zoom + full button equivalents, focusable canvas, annotations panel on every tier, attribution line, Showcase hero entrance in reserved box); Simulation frame (poster-first, bounded-wait fallback, params relayed via protocol); Poster fallback card (first-class content styling, counts as viewed, never error-styled).
UX-DR16: Capability tiers & degradation ladder — Showcase/Full/Constrained/Floor with feature-based detection (demote-when-unsure), auto-load default everywhere, tap-to-load with transfer-size labels only under data-saver signals, at most one heavy Block live (release on leave, cached re-load without re-prompt), budgeted lazy posters, completion tier-independent, Teacher previews the Floor.
UX-DR17: Moodle Embedding Contract — inherit page scroll, container-width fluid single column, self-managed height, no nested scrollbars, namespaced styles with no global resets, no layout shift (reserved media boxes, own-top-edge scroll on navigation), opaque card look on light themes, one instance per page, browser back stays Moodle's; Moodle mobile app gets the designed browser hand-off state.
UX-DR18: Voice & Tone — every user-facing string externalised (NFR-8/AD-20) in plain, warm, honest English; limit/quota copy interpolated from tenant config (exemplar set in EXPERIENCE.md); the FR-28 AI label verbatim and never reworded; no hype, no blame.
UX-DR19: State patterns catalogue — every row of EXPERIENCE.md § State Patterns implemented as a designed state (cold-load skeletons text-first, generation states, budget-pause, block-regenerating, save-failed, session-ending, check-failed, publish-succeeded, discard confirm, lesson-not-available, unknown-block omission, major-version can't-play, flag-off poster render, connectivity loss, score syncing, attempts exhausted, completion, version pinning, mid-lesson reload, diagram message states, empty queues).
UX-DR20: Diagram chat message (block_edon_ai) — request → generating → sanitised SVG card with always-visible AI label + "Report this diagram" (≥ 48 px, disabled after reporting with confirmation — 48 px ratified at sign-off 2026-07-18); accessible name = label + request text + description; cache hits render instantly and identically; all limit/quota/failure states as humane chat replies via the chat's live region; no diagram affordance when flagged off.
UX-DR21: Moodle-native surfaces (theme-inherited, standard Moodle renderers per WI-MOD-0) — Lesson picker (Published Versions for the course; completion options + quiz attempt limits configured here) and the "Open Lesson Studio" teacher entry point minting the Launch Token (new-tab launch).
UX-DR22: Accessibility floor — WCAG 2.1 AA scoped per OQ-7 (full AA on controlled surfaces; text-alternative contract + best-effort on AI content); full keyboard operability incl. Simulation params (native controls, checked pre-publish); `aria-live=polite` on async changes; visible focus indicators; touch targets ≥ 48 px Player/chat, ≥ 44 px authoring; color+glyph+text feedback pairing; `lang` from the script's language tag; toggle state exposure; policy-disabled controls associated with their explanatory banner.
UX-DR23: Interaction primitives & motion — tap-only required gestures, no swipe navigation, no hover-only affordances, no autoplaying audio, overlays max one deep with focus trap/return, Esc closes topmost; banned list enforced; tiered motion budget (no continuous animation below Showcase; Showcase motion ≤ 300 ms transitions, shimmer skeletons, hero entrance, green-family quiz celebration ≤ 600 ms — all in the lazy chunk, all suppressed by `prefers-reduced-motion`, never touching gold governance signals).

### FR Coverage Map

- FR-1: Epic 1 — Lesson Script Schema v1.0 package (Story 1.1)
- FR-2: Epic 1 — versioning rules + forward-compat fixture corpus (1.1); player-side behavior exercised in Epic 4 (4.9)
- FR-3: Epic 1 — validators + docs as first-class package (1.1); consumed by every producing/rendering epic
- FR-4: Epic 2 — grounded generation intake (2.3, 2.6); tenant-scoped retrieval (2.1)
- FR-5: Epic 2 — schema-conforming pipeline, no partial Drafts (2.2, 2.3)
- FR-6: Epic 2 — per-Block Citations stored (2.3); Teacher display Epic 3 (3.2); Student Sources Epic 4 (4.7)
- FR-7: Epic 2 — Draft persistence + idempotency (2.4); whole-Lesson Regeneration entry Epic 3 (3.5)
- FR-8: Epic 2 — async jobs + progress (2.5, 2.6)
- FR-9: Epic 3 — faithful preview overlay (3.6)
- FR-10: Epic 3 — editing/reorder/delete/discard + Regeneration framework (3.3, 3.5); per-type wiring Epics 7 (7.2), 9 (9.3), 10 (10.4)
- FR-11: Epic 3 — explicit immutable publication (3.7)
- FR-12: Epic 3 — Review Gate enforcement (3.7); Student-side delivery paths Epic 4 (4.2, 4.9)
- FR-13: Epic 4 — Slide/Narration/Quiz rendering (4.3–4.5); Diagram Epic 7 (7.2); Model3D Epic 9 (9.4); Simulation Epic 10 (10.5)
- FR-14: Epic 4 — NarrationProvider pair + transcript floor (4.4)
- FR-15: Epic 4 — instant client feedback + server-authoritative scoring (4.5, 4.6)
- FR-16: Epic 9 — Curated Model Library + viewer (9.1–9.4)
- FR-17: Epic 10 — sandbox, protocol, checks, frame (10.1–10.5)
- FR-18: Epic 4 — tier/degradation framework + budgets CI (4.1, 4.8); per-asset budgets Epics 9/10; perf gates Epic 11 (11.2)
- FR-19: Epic 7 — platform diagram channel (7.3); chat surface Epic 8 (8.1)
- FR-20: Epic 7 — the sanitisation gate (7.1)
- FR-21: Epic 7 — cache, Rate Limits, Quotas (7.3, 7.4)
- FR-22: Epic 5 — picker/session APIs (5.3) + Epic 6 — activity + embed (6.2, 6.3)
- FR-23: Epic 4 — attempt semantics (4.6, 4.7); Epic 5 — outbox (5.4); Epic 6 — scheduled task + gradebook (6.4)
- FR-24: Epic 5 — tenant server-to-server auth (5.2); pseudonym foundation Epic 1 (1.4)
- FR-25: Epic 1 — TenantContext + RLS substrate (1.3); binds every story's DoD
- FR-26: Epic 1 — governance subsystem + Operator config (1.6, 1.8); exhaustion UX Epics 2/3 banners, Epic 7 cache-only
- FR-27: Epic 1 — events + telemetry substrate (1.7); per-feature emission in Epics 2–10; computability verified Epic 11 (11.6)
- FR-28: Epic 7 — governance loop (7.3, 7.5, 7.6); label/report surface Epic 8 (8.2)
- FR-29: Epic 5 — verification + sessions (5.1); Epic 6 — entry point + minting (6.5)
- AMD-1: Epic 3 — publish-time TTS (3.8); Epic 4 — PregeneratedAudioProvider (4.4)
- AMD-2: Epic 8 — WI-CHAT-4 course-scoped chat embed (8.3)

**NFR coverage:** NFR-1 → Epics 2 (timing telemetry), 11 (verification). NFR-2 → Epics 4, 9, 10, 11. NFR-3 → Epics 1 (secrets, rotation), 5 (per-tenant CORS), 7 (sanitisation), 10 (sandbox). NFR-4 → Epics 1, 3, 4. NFR-5 → Epic 1. NFR-6 → Epics 1, 2, 7 (structural: replay path zero-LLM verified 11.6). NFR-7 → Epics 1 (licence gate), 6 (GPLv3 thin), 9 (asset licences). NFR-8 → Epics 1 (lint gate), all UI stories, 11 (audit). NFR-9 → Epics 1 (adapter types, pseudonyms, retention), 7 (identity-stripping).

**UX-DR coverage:** UX-DR1–2 → Epics 2/3 (authoring), 4 (player chrome), 11 (fonts chunk). UX-DR3 → Epics 2/3. UX-DR4–5 → Epic 2. UX-DR6–12 → Epic 3. UX-DR13 → Epic 7. UX-DR14–17, 19 → Epic 4 (+9/10 per block type). UX-DR18 → all UI stories + Epic 11 audit. UX-DR20 → Epic 8. UX-DR21 → Epic 6. UX-DR22 → cross-cutting + Epic 11 (11.4). UX-DR23 → Epics 4, 11.

**AR coverage:** AR-1..9, 14, 18–20, 25, 26, 31, 32 → Epic 1. AR-17, 24, 27 → Epic 2. AR-5, 23 → Epic 3. AR-10, 11, 15, 22 → Epic 4. AR-16 → Epic 5. AR-13, 21 → Epic 7. AR-12 → Epic 10. AR-29 → Epics 9, 10. AR-28 → milestone gates + Epic 11. AR-30 → non-blocking by construction (config defaults everywhere; freecode activation excluded from scope).

## Epic List

*Approved by the stakeholder 2026-07-18 (this session), with two recorded adjustments: (1) milestone preview checkpoints are formal gate exit criteria (metadata below, not stories); (2) Epic 2's recorded-fixtures story consumes stakeholder-produced fixture files (see Story 2.1). Every story additionally carries the project-context §7 DoD: structured tenant-scoped logs, telemetry emitted, mandatory unit tests for [HARD]-rule protectors, `.env.example` updated if config changed.*

*All `[ASSUMPTION]` tags in this document were confirmed by john at the 2026-07-18 implementation-readiness sign-off (see `implementation-readiness-report-2026-07-18.md` §7); they stand as accepted defaults.*

### Epic 1: Lesson Script Schema & Platform Foundation (M1)
Teachers, Students, and the Operator get the product's contract and rails: the versioned Lesson Script Schema as the keystone package, plus the deployable, tenant-isolated, governed, observable platform substrate every later epic rides. The schema package is the first story, per stakeholder directive.
**FRs covered:** FR-1, FR-2, FR-3; substrate for FR-25, FR-26, FR-27 (+ AR-1..9, 14, 18–20, 25, 26, 31, 32)

### Epic 2: Grounded Generation on Recorded Fixtures (M1)
A Teacher submits a topic and receives a cited, schema-valid Draft (Slide/Narration/Quiz walking skeleton) through the async pipeline with the block-by-block progress showpiece — developed entirely on recorded retrieval fixtures, with a thin final story switching to the live edon-rag endpoint (WI-RAG-0 **delivered 2026-07-18**, edon-rag v2.1.0 — the switch story is unblocked).
**FRs covered:** FR-4, FR-5, FR-6, FR-7, FR-8 (+ AR-17, 24, 27)

### Epic 3: Review Gate & Publish, incl. publish-time TTS (M2)
A Teacher reviews, edits, reorders, previews, and explicitly publishes a Draft into an immutable, asset-frozen, TTS-voiced Published Version — the Review Gate made real, with draft durability and concurrency guarantees.
**FRs covered:** FR-9, FR-10 (framework), FR-11, FR-12; AMD-1 server side (+ AR-5, 23)

### Epic 4: Player Core (M2)
A Student plays a Published Version end-to-end in the embeddable Player — slides, narration (pre-generated audio + fallback), quizzes with instant feedback and server-authoritative scoring, attempts, resume, completion — degrading gracefully across the capability tiers.
**FRs covered:** FR-13 (core types), FR-14, FR-15, FR-18 (framework), FR-12 (delivery); FR-23 (attempt semantics); AMD-1 player side (+ AR-10, 11, 15, 22)

### Epic 5: Platform LMS Edge (M3)
The platform speaks its LMS-agnostic integration surface: Launch Token verification and Authoring Sessions, tenant server-to-server auth with rotation, lesson picker and playback session APIs, and the pull-and-ack delivery outbox — everything mod_edonlesson needs, Moodle-free.
**FRs covered:** FR-22, FR-23, FR-24, FR-29 (platform side) (+ AR-16)

### Epic 6: mod_edonlesson Companion Plugin (M3 — companion repo, GPLv3)
A Teacher places Published Versions in courses and launches authoring from Moodle; Students play embedded lessons whose grades and completion land in the gradebook — the thin plugin, including production-theme style-isolation verification (M3 gate item).
**FRs covered:** FR-22, FR-23, FR-24, FR-29 (Moodle side) (+ UX-DR21, WI-MOD-0..3)

### Epic 7: Diagram Blocks & the Governed Student Diagram Channel (M4)
Lessons gain reviewed Diagram Blocks, and Students gain on-demand labelled diagrams in chat — grounded, sanitised, cached, rate-limited, quota-bound, labelled, reportable, and reviewable: the one Review-Gate bypass fully inside its governance loop.
**FRs covered:** FR-19, FR-20, FR-21, FR-28; Diagram slices of FR-10/FR-13 (+ AR-13, 21)

### Epic 8: block_edon_ai Companion Enhancement (M4 — companion repo)
The existing chat renders the diagram experience (minimal surface: call the platform, render the sanitised result) and embeds course-scoped on the lesson activity page (WI-CHAT-4) — Live Q&A beside every lesson.
**FRs covered:** FR-19 (surface), FR-28 (label/report surface); AMD-2 (+ UX-DR20, WI-CHAT-1..4)

### Epic 9: Model3D Blocks & the Curated Library (M5 — **blocked on OQ-6: ≥ 20 stakeholder-curated models**)
Teachers get lessons with interactive, annotated, licence-attributed 3D models selected from the Curated Model Library; the library gets its ingest pipeline and its stakeholder-curated seed.
**FRs covered:** FR-16; Model3D slices of FR-10/FR-13/FR-18 (+ AR-29)

### Epic 10: Simulation Blocks, Template-First (M5)
Students manipulate parameter-driven simulations that ran the gauntlet: locked sandbox, pinned postMessage protocol, headless pre-publish checks, template library as the launch mode — freecode supported behind its tenant flag, activation stakeholder-gated and non-blocking.
**FRs covered:** FR-17; Simulation slices of FR-10/FR-13/FR-18 (+ AR-12, 29)

### Epic 11: Showcase Polish & Launch Hardening (M6)
The canonical Showcase experience lands (webfonts, motion, hero entrance, celebration) inside enforced budgets, and the platform proves launch-ready: perf gates, i18n and AA audits, monitoring, runbooks, the weekly ops checklist, and pilot-readiness verification.
**FRs covered:** polish/verification slices of NFR-1, NFR-2, NFR-8; UX-DR1/2/22/23 (+ AR-26, 28)

## Milestone Gates — formal exit criteria (stakeholder adjustment, 2026-07-18)

*Each gate closes with a **private pilot-college preview**: a staged demonstration on the staging environment (synthetic tenant + invited real reviewers) to the stakeholder and invited pilot-college lecturer(s). Recorded here as gate metadata binding epic completion — deliberately not stories. Launch after M6 = sponsored/paid pilot of ≤ 5 colleges.*

- **M1 exit (Epics 1–2):** Demonstrable: a Teacher (dev-token launch) submits topic + guidance and watches the block-by-block assembly produce a cited, schema-valid Slide/Narration/Quiz Draft on recorded fixtures; identical resubmission returns the same Draft without spend; governance refusal (budget pause) and telemetry rows shown. Schema package validates the full fixture corpus (incl. unknown-block/future-version fixtures) in CI. **WI-RAG-0 explicitly not required at this gate** — recorded fixtures are the sanctioned path. Audience: stakeholder + invited pilot-college lecturer(s).
- **M2 exit (Epics 3–4):** Demonstrable: the same Draft reviewed, edited, reordered, previewed (incl. Low-spec view), and published as immutable v1 with publish-time TTS audio; the Player plays it end-to-end in a plain host page via `EdonPlayer.mount` — narration (audio + fallback), quiz with instant feedback and server-authoritative score, reload-resume, completion summary; republish yields v2 with v1 still playable. Audience: stakeholder + invited pilot-college lecturer(s).
- **M3 exit (Epics 5–6):** Demonstrable on staging Moodle with the production (Almondb-based) theme: "Open Lesson Studio" launch → Launch Token → same-Draft relaunch; activity placement via the Lesson picker; embedded playback with **style isolation against the production theme verified** (gate item F4); completion + grade landing in the gradebook via outbox drain within the demo window; writeback failure/retry events shown. Audience: stakeholder + pilot-college Moodle admin + lecturer(s).
- **M4 exit (Epics 7–8):** Demonstrable: a lesson with a reviewed Diagram Block; a Student requesting a labelled diagram in block_edon_ai chat (fresh + instant cache hit), hitting the Rate Limit and daily Quota with humane copy; report → Teacher review queue → Mark invalid evicting the cache; the course-scoped chat presented beside the lesson activity (WI-CHAT-4). Audience: stakeholder + pilot-college lecturer(s) + student volunteers.
- **M5 exit (Epics 9–10):** Demonstrable: a published lesson containing all six Block types; Model3D from the **≥ 20-model stakeholder-curated seed library** (licence attribution visible) with orbit/zoom/annotations; a template Simulation manipulated live, incl. a failing simulation blocked at publish with a per-Block reason; poster fallbacks under data-saver/Floor conditions. **Gate cannot open before the OQ-6 seed bar is met.** Audience: stakeholder + pilot-college science lecturer(s) + student volunteers.
- **M6 exit (Epic 11):** Demonstrable: the Showcase-canonical experience (webfonts, motion, hero entrance, quiz celebration) within budgets on a modern phone; blocking perf check green in CI; AA audit closed; weekly ops checklist executed live (spend alerts, writeback_overdue review, diagram-report queue, key rotation); SM-1..SM-5 + counter-metrics + the OQ-18 adoption metric computed from stored data. Exit = launch-ready for the ≤ 5-college sponsored pilot. Audience: stakeholder + pilot-college leadership.

## Epic 1: Lesson Script Schema & Platform Foundation

Teachers, Students, and the Operator get the product's contract and rails: the versioned Lesson Script Schema as the keystone package, plus the deployable, tenant-isolated, governed, observable platform substrate every later epic rides.

### Story 1.1: Lesson Script Schema v1.0 Package

As a renderer or pipeline author,
I want the versioned Lesson Script Schema shipped as a first-class validated package with fixtures and documentation,
So that every producer and consumer shares one content contract whose Published Versions stay playable forever.

**Acceptance Criteria:**

**Given** the freshly bootstrapped monorepo `[ASSUMPTION: this story includes the minimal repo bootstrap /schema needs; the full scaffold is Story 1.2]`
**When** the `/schema` package is built
**Then** JSON Schema 2020-12 documents define Lesson Script v1.0 (`"schema": "1.0"`) with lesson metadata — tenant, course reference, `curriculumRef {value, source: "pipeline"|"teacher"}`, version, Citations — and an ordered Block list covering all six MVP Block types (FR-1)
**And** camelCase field casing throughout; Narration Blocks carry optional `audioRef`; Diagram Blocks and Model3D/Simulation posters carry `altText`/`longDescription`; every heavy-asset reference carries `transferSize` in bytes; the citation object requires only `sourceChunkId`, `documentTitle`, `excerpt` with `locator`/`documentId`/`tags` optional (AD-2)
**And** Simulation Blocks define `mode: "template" | "freecode"` with `templateId`/`bundleRef` payload fields (AD-12).

**Given** the shared fixture corpus (valid scripts, invalid scripts, an unknown-Block-type fixture, future minor- and major-version fixtures, a no-locator citation fixture)
**When** the `js/` (ajv) and `py/` (jsonschema) validator wrappers run in CI
**Then** both validators agree on every fixture, and a script missing schema version, tenant, or version metadata fails validation (FR-1, FR-2)
**And** the version-mismatch semantics are documented: minor = additive only (ignore unknowns), major = defined cannot-play state applying only to scripts newer than the player build (A-26).

**Given** the package documentation in `/schema/docs`
**When** a renderer author reads it without access to pipeline code
**Then** each Block type is specified sufficiently to implement a renderer against the package alone (FR-3)
**And** the docs carry the version-bump + migration/compatibility-note rule and the reserved-extensions record (V2 dialogue types, V3 streaming — record only, do not design).

### Story 1.2: Monorepo Scaffold, CI Gates, and Deploy Skeleton

As a platform developer,
I want the greenfield monorepo with the full CI gate set and a deployable skeleton,
So that every subsequent story lands on enforced rails instead of convention.

**Acceptance Criteria:**

**Given** the spine's source tree layout
**When** the scaffold lands
**Then** `backend/` (FastAPI app + uvicorn, `core/`–`adapters/`–`api/`–`workers/` layout, health endpoint), `player/`, `authoring/`, `docs/` (adr, integrations, runbooks) exist per AR-31, with `uv`-managed pinned Python deps (lockfile committed) and npm workspaces for JS
**And** the import-linter contract fails CI if `core` imports `api/`, `adapters/`, `workers/`, or any framework/queue/vendor SDK (AD-1).

**Given** the CI pipeline
**When** it runs on a branch
**Then** pytest + ruff, Vitest + ESLint + Prettier, and the Playwright scaffold execute; a `.ts`/`.tsx` file anywhere in `/player`, `/authoring`, or `/schema/js` fails the no-TypeScript lint gate; a non-allowlisted direct or transitive dependency in either lockfile fails the licence-audit gate; the i18n lint gate (no bare string literals in JSX text positions, no inline user copy in API response builders) is active (AD-20, AR-25)
**And** `budgets.json` exists at repo root with its own JSON Schema in `/schema` and is consumed by a CI stub so later budget checks plug in (AD-11).

**Given** the two deferred first-epic decisions (CI provider; deploy transport)
**When** this story completes
**Then** both are decided and recorded in `/docs` `[ASSUMPTION: GitHub Actions as the spine's working assumption unless john overrides]`
**And** the staging VPS runs the systemd unit set (api, worker templates, nginx + TLS) with a deploy runbook draft and a maintained `.env.example`.

### Story 1.3: Tenant Substrate — TenantContext, RLS, Migrations Baseline

As the Operator,
I want every data path tenant-scoped at both the application and the database,
So that cross-tenant access paths cannot exist even by accident.

**Acceptance Criteria:**

**Given** the Alembic baseline migration with the `tenants` table
**When** any repository, asset-path helper, or cache-key helper is called
**Then** it requires a `TenantContext` resolved from the authenticated credential (never from request params), and PostgreSQL RLS is active on every tenant-owned table via the per-request session GUC (AD-6, FR-25).

**Given** a new migration adding a tenant-owned table without an RLS policy in the same migration
**When** migration CI runs
**Then** the build fails (AR-25).

**Given** two tenants with data in place
**When** tenant A's context queries lessons, cache entries, or assets
**Then** tenant B's rows are never returned — proven by an automated cross-tenant isolation test
**And** logging middleware binds `tenant_id` + user pseudonym to every log line (no bare prints).

### Story 1.4: Identity & Credentials — Five Kinds plus Dev Token CLI

As a Teacher, Student, or Operator,
I want exactly five scoped, rotatable credential kinds with config-driven lifetimes,
So that access is least-privilege and secrets stay hygienic from day one.

**Acceptance Criteria:**

**Given** the AD-14 credential set
**When** implemented
**Then** tenant API keys (hashed, two concurrently valid, rotation without downtime), Launch Token verification (JWT HS256 per-tenant secret, 120 s, single-use `jti`, URL-fragment transport), Authoring Sessions (HttpOnly cookie, 8 h absolute), Playback tokens (opaque, 24 h, lesson+attempt-scoped), and Operator keys (named, CLI-issued, valid only on `/operator/*`, every use audited) all exist with lifetimes as config (NFR-3)
**And** `user_pseudonym = HMAC-SHA256(per-tenant salt, lms_user_id)` is the identity used everywhere outside the identity module, session/attempt tables, and delivery outbox (NFR-9).

**Given** a developer without a Moodle instance
**When** they run the dev-only token-minting CLI
**Then** it mints Launch Tokens on the same JWT code path, and is disabled by prod config — making every pre-Moodle epic testable (AD-14).

**Given** an expired or tampered Launch Token
**When** presented
**Then** verification fails closed with a machine-coded error and no partial access (FR-29).

### Story 1.5: LLM Adapter — Two Drivers, Per-Workload Config

As the platform,
I want all model access through one provider-agnostic async adapter,
So that model migration is a config change and no untelemetered spend path exists.

**Acceptance Criteria:**

**Given** per-workload config (`lesson_generation`, `simulation_generation`, `diagram_generation`, `tts`; `embeddings` present in config but never called)
**When** a consumer calls the adapter
**Then** provider, model, endpoint, and params come from config only — no model identifier or endpoint is hardcoded anywhere outside configuration ([HARD] §3)
**And** exactly two drivers exist: `openai-compatible` (base_url per provider) and `anthropic-native` (translating), plus the OpenAI-compatible speech surface for `tts` under the same discipline (AD-3).

**Given** the adapter request types
**When** inspected
**Then** they carry no identity fields — only the mandatory `governance_ref = (action_type, accounting_ref)`; only the telemetry writer resolves `accounting_ref` to tenant/pseudonym (NFR-9).

**Given** a provider swap for one workload in config
**When** the test suite exercises it against a stub provider
**Then** consuming services need zero code changes — the ADR-002 benchmark and the self-hosting migration ride this property (AR-30; the benchmark itself is stakeholder-owned and blocks nothing)
**And** every call emits the fixed Cost Telemetry row (`tokens_in, tokens_out, computed_cost, tenant_id, user_pseudonym, workload, cache_hit, latency_ms, model_id, request_ref`), unit-tested against the contract (AD-19).

### Story 1.6: Governance Subsystem — Reserve → Settle

As the Operator,
I want quotas, rate limits, and budgets enforced in one subsystem over one action vocabulary,
So that no LLM-spending path escapes policy and future generation types are policy rows, not new code.

**Acceptance Criteria:**

**Given** the `action_type` vocabulary
**When** an LLM-spending action is intaken
**Then** the pre-enqueue/pre-request governance check returns machine codes `budget_paused | quota_exhausted | rate_limited` for UIs to render, and the adapter-path reserve→settle backstop reserves before the call and settles with real telemetry cost after — failed-job spend settles too (A-29, AD-8).

**Given** a tenant whose calendar-month Budget Ceiling exhausts
**When** enforcement triggers
**Then** OQ-9 semantics hold verbatim: generation intake pauses with explicit notice, diagrams degrade to cache-only, replay of Published Versions is never blocked; a job already queued fails fast at fetch with `budget_paused` and no spend; the default per-tenant generation concurrency of 1 bounds overrun at exactly one in-flight job (FR-26)
**And** cache hits charge nothing against any policy (FR-21).

**Given** the [HARD]-rule protection requirement
**When** the test suite runs
**Then** unit tests cover quota, rate-limit, and budget enforcement, reserve→settle including failure settlement, and the machine-code surface (project-context §7).

### Story 1.7: Structured Events, Cost Telemetry Store, and Retention

As the Operator,
I want the closed event taxonomy and telemetry persisted with every state change,
So that all success metrics are computable from stored data alone and retention is enforced by policy.

**Acceptance Criteria:**

**Given** any state mutation
**When** it commits
**Then** it went through a core use-case and its FR-27 Structured Event inserted in the same transaction (AD-7), with the closed canonical taxonomy (PRD FR-27 list + `diagram_review_completed`, `diagram_invalidated`, `operator_action`, `cost_alert`, `writeback_overdue`); ad-hoc event strings are rejected at review/CI `[ASSUMPTION: enforced by a taxonomy enum + test, the mechanical reading of "closed"]`.

**Given** stored events, telemetry, and domain records
**When** SM queries are drafted
**Then** per-Tenant and per-Lesson cost is computable from telemetry alone, and diagram cache hits emit zero-cost rows without token fields (AD-19).

**Given** `retention.yaml` (default 12 months)
**When** the nightly maintenance job runs
**Then** expired logs/events age out per config, and the processor record exists at `/docs/processors.md` (NFR-9).

### Story 1.8: Operator Tenant Provisioning & Policy Configuration

As the Operator,
I want to create tenants and set their budgets, quotas, rate limits, flags, and origins via CLI and audited endpoints,
So that pilot colleges can be onboarded and governed without code changes (UJ-4).

**Acceptance Criteria:**

**Given** the operator CLI + `/operator/*` router (separate DB role, explicit `tenant_id` parameter)
**When** the Operator creates a tenant, issues/revokes API keys, or sets Budget Ceiling, generation/diagram Quotas, per-user Rate Limits (platform defaults, tenant-overridable), feature flags, or CORS origins
**Then** each action takes effect without redeploy, and every action emits an audited `operator_action` event (AD-6, FR-26, A-14)
**And** `feature.diagrams` and `feature.simulation_blocks` exist as flags evaluated at generation intake and playback bootstrap; flags never alter delivered script content (AD-18).

**Given** policy values anywhere in the codebase
**When** reviewed
**Then** none are code constants — all live in platform config files or tenant config rows (AD-18).

## Epic 2: Grounded Generation on Recorded Fixtures

A Teacher submits a topic and receives a cited, schema-valid Draft through the async pipeline with visible block-by-block progress — developed on recorded retrieval fixtures so WI-RAG-0 never blocks the epic.

### Story 2.1: edon-rag Retrieval Client on Recorded Fixtures

As the generation pipeline,
I want a RagClient port implementing the v1.2 course-scoped retrieval contract, backed by recorded fixture files,
So that grounded generation develops and tests deterministically before the live endpoint exists.

**Acceptance Criteria:**

**Given** the contract in `docs/integrations/edon-rag-retrieval.md` (v1.2: `POST /api/courses/{moodle_course_id}/retrieve`, `x-api-key` auth, ranked Grounding Chunks with metadata/citations)
**When** the fixture-backed adapter is used
**Then** it loads sample response JSON files from the designated `fixtures/` folder, and retrieval is tenant- and course-scoped exactly as the live adapter will be (FR-4, I-4).

**Given** the fixtures provenance (stakeholder adjustment, 2026-07-18)
**When** stories in this epic consume fixtures
**Then** they are written against the `fixtures/` folder contract: **real fixture files — sample JSON responses recorded from the production WI-RAG-0 endpoint (edon-rag v2.1.0) — landed 2026-07-18 at `fixtures/edon-rag/`** and are the authoritative fixture set; synthetic interim fixtures are superseded, and the recorded files must be consumed **without code changes**
**And** a fixture-shape validation test fails if any fixture departs from the v1.2 contract — strict on the required response set, tolerant of additive `metadata` keys (v1.2 allows them; sign-off 2026-07-18).

**Given** a retrieval result below the pipeline's score floor
**When** consumed
**Then** the ungrounded-failure path is exercisable in tests (A-5 wiring lands in 2.3).

### Story 2.2: Pipeline Engine as Configuration

As the platform,
I want the pipes-and-filters generation engine driven entirely by versioned config,
So that prompt and stage tuning never requires a code release.

**Acceptance Criteria:**

**Given** `pipeline.yaml` + prompt files (language-keyed, stable-prefix-ordered for provider prefix caching)
**When** the engine runs a job
**Then** stages, prompts, retrieval params, repair policy, and per-Block fan-out concurrency all come from config; a stage failure gets exactly one repair retry, then the whole job fails — no partial Draft ever persists (FR-5, AD-17).

**Given** the golden-path integration test on recorded LLM fixtures
**When** CI runs
**Then** a full pipeline run produces a validated Draft from fixture responses, and a config-only prompt edit changes behavior without code changes (project-context §7).

### Story 2.3: Walking Skeleton — Plan + Slide/Narration/Quiz Stages with Citations

As a Teacher,
I want my topic turned into a cited Draft of slides, narration, and quizzes,
So that I can see my institution's curriculum become lesson content.

**Acceptance Criteria:**

**Given** a Generation Job with topic, Course Context, and optional guidance
**When** the pipeline runs
**Then** the plan stage mints stable per-Block slot ids preserved by all later writers (AD-23), per-Block content stages produce Slide, Narration, and Quiz Blocks, and the assembled script passes the schema package validator before any Draft persist (FR-5, FR-3)
**And** every Block carries embedded Citations to its Grounding Chunks (also projected to the query table, embedded copy authoritative), and the Draft carries at least one Citation (FR-6)
**And** Quiz Blocks include Teacher-editable accepted-answer lists and feedback; Narration text carries the language tag (OQ-4, NFR-8).

**Given** retrieval returning nothing above the score floor
**When** the job runs
**Then** it fails `ungrounded` with a Teacher-readable reason — never an uncited Draft (A-5)
**And** a request missing topic or course context is rejected with a clear message before any job is enqueued (FR-4).

### Story 2.4: Draft Persistence & Idempotency

As a Teacher,
I want identical requests to return my existing Draft while regeneration stays explicit,
So that accidental resubmission never spends money or overwrites work.

**Acceptance Criteria:**

**Given** the single `core/text.py: normalise_key` implementation (Unicode NFC → casefold → whitespace collapse → trim → iterative trailing-punctuation strip), with the shared fixture vector in `/schema` and a CI assertion that no second implementation exists (AD-17)
**When** an identical generation request (tenant, course context, topic, guidance) arrives while a matching Draft exists
**Then** the existing Draft is returned with no LLM call and no governance charge (FR-7).

**Given** an explicit whole-Lesson Regeneration action
**When** submitted
**Then** the pipeline re-runs, bypassing the idempotency cache — and no code path regenerates without an explicit Teacher action (FR-7).

**Given** Draft persistence
**When** a job completes
**Then** exactly one mutable Draft per Lesson exists with monotonic `revision` (AD-5), and `lesson_generated` / `generation_failed` events emit with `scope: lesson` (AD-7).

### Story 2.5: Async Jobs with Per-Block Progress over SSE

As a Teacher,
I want generation queued with live per-Block progress I can leave and return to,
So that a five-minute job never holds my browser hostage.

**Acceptance Criteria:**

**Given** a generation request passing the governance pre-check
**When** intake commits
**Then** the job is enqueued on Procrastinate's `generation` queue in the same transaction as the domain write (AD-4), the API returns immediately (FR-8), and a `budget_paused | quota_exhausted | rate_limited` refusal returns its machine code instead (AD-8).

**Given** a running job
**When** stages execute
**Then** `job_progress` rows are written per the AD-24 shape (`job_id, block_id, stage, state ∈ {pending, running, repaired, done, failed}, display_key, at`), and the SSE stream serves snapshot-then-tail with named `progress` events and a terminal `job_completed | job_failed` (AD-24)
**And** `display_key` resolves through the AD-20 language catalog, and absent fine-grained rows degrade consumers to the coarse A-8 states — never a broken stream.

**Given** a failed job
**When** the Teacher observes it
**Then** the failure reason is Teacher-readable, and no Student-visible artifact exists (FR-8).

### Story 2.6: Authoring SPA Foundation — Generate Form + Progress Card

As a Teacher,
I want to start generation from a two-field form and watch my lesson assemble block by block,
So that I need no prompt-engineering skill to author.

**Acceptance Criteria:**

**Given** the Authoring SPA scaffold (Vite + React JSX, react-router, thin fetch wrappers, DESIGN.md tokens, i18n catalog wiring) launched via the dev token-minting CLI `[ASSUMPTION: dev-token launch is the sanctioned entry until Epic 5/6 deliver the real Moodle launch — AD-14's stated purpose]`
**When** the Teacher opens the Generate form
**Then** it shows exactly Topic (required) + Guidance (optional) in a 640 px column, with the Course Context as a read-only locked chip from the launch credential — no course picker exists (FR-4, FR-29, UX-DR4)
**And** submitting without a topic is rejected inline; submitting an identical request reroutes to the existing Draft with an announced info banner and focus move (FR-7).

**Given** a submitted job
**When** the progress card renders
**Then** it shows block-by-block assembly (glyph + title skeleton → filled row) from the SSE stream, degrades to the plain coarse-state card when per-Block events are absent, shows elapsed time, sets a leave-safe few-minutes expectation (never a hard number), and on failure shows the readable reason plus an explicit "Try again" (UX-DR5)
**And** async state changes announce via `aria-live=polite`; every string is externalised (UX-DR22, AD-20).

**Given** a tenant whose budget is exhausted
**When** the Teacher views the form
**Then** the persistent gold budget-pause banner shows with honest copy, the form is disabled and programmatically associated with the banner, and replay/review remain unaffected (FR-26, UX-DR3).

### Story 2.7: Live Retrieval Switch — Thin (UNBLOCKED 2026-07-18: WI-RAG-0 delivered, edon-rag v2.1.0)

As the platform,
I want generation flipped to the production edon-rag endpoint the moment it exists,
So that pilot generation grounds in real corpora with zero rework.

**Acceptance Criteria:**

**Given** WI-RAG-0 delivered on the edon-rag side (the course-scoped retrieval endpoint live in production)
**When** the live adapter is enabled by configuration
**Then** generation runs against `POST /api/courses/{moodle_course_id}/retrieve` with per-tenant `x-api-key` auth and no code changes in consuming services (AR-27).

**Given** the staging smoke tenant
**When** a live-retrieval generation runs
**Then** the response is validated against the v1.2 contract; any discrepancy against the recorded fixtures is logged and raised as an integration work item — never an assumed edit to edon-rag (project-context §8)
**And** recorded-fixture mode remains the CI golden path permanently (AD-17 testing floor).

## Epic 3: Review Gate & Publish (incl. publish-time TTS)

A Teacher reviews, edits, reorders, previews, and explicitly publishes a Draft into an immutable, asset-frozen, TTS-voiced Published Version — the Review Gate made real.

### Story 3.1: Course Home & College Library

As a Teacher,
I want my course's lessons and my college's published library in one place,
So that I can manage my own work and reuse my colleagues'.

**Acceptance Criteria:**

**Given** a launched Authoring session
**When** Course home renders
**Then** it lists the Teacher's own Drafts (private, creator-owns) and the Tenant's Published Versions for the launch course as Lesson cards with status chips and the version history line; the header carries the course chip on every surface (OQ-13, UX-DR12)
**And** the branded Empty state renders when the course has no lessons.

**Given** the College library tab
**When** browsed
**Then** it lists the Tenant's Published Versions across courses with "Duplicate as my draft"; duplicating creates a new Draft owned by the duplicating Teacher, leaving the original untouched (OQ-13).

**Given** a Tenant Admin opening another Teacher's lesson
**When** the Review Workspace loads
**Then** a persistent info banner names the owner — visible, never blocking (OQ-13)
**And** a non-owner non-admin Teacher gets the read view with Duplicate only; edit/discard/publish are restricted to owner + Tenant Admin (FR-10).

### Story 3.2: Review Workspace — Rail, Editor, Citations Layout

As a Teacher,
I want a three-pane workspace showing every Block and its provenance,
So that review is a scan, not a hunt.

**Acceptance Criteria:**

**Given** a Draft opened for review
**When** the workspace renders at ≥ 1024 px
**Then** the three panes show (rail ~280 px / fluid editor / citations ~320 px collapsible), collapsing per breakpoint (768–1023: citations slide-in sheet; < 768: horizontal block strip) with nothing desktop-only (UX-DR6)
**And** panes are named landmarks with a skip-to-editor link.

**Given** the Block rail
**When** navigated
**Then** it is a single tab stop with arrow-key traversal; items show index, type glyph, excerpt, mini status chip; drag reorder has always-visible-on-focus button equivalents; the session-local unseen dot (gold fill in accent-ink ring) appears on Blocks not yet opened and is exposed programmatically ("not yet opened since generation") (UX-DR6)
**And** status chips follow the defined lifecycle (Draft/Published/Edited/Needs review/Check failed; "Needs review" clears when the Block is opened, session-scoped, never persisted).

**Given** the Citations panel
**When** a Block is selected
**Then** its per-Block citation cards render (excerpt → Grounding Chunk metadata), collapsible (FR-6, UX-DR9).

### Story 3.3: Block-Level Text Editing with Revalidation

As a Teacher,
I want to edit exactly what the approved editability map allows,
So that I can correct AI output before any Student sees it.

**Acceptance Criteria:**

**Given** the A-28 editability map
**When** the Block editor renders per type
**Then** text fields are editable for Slide, Narration, Quiz (questions, options, accepted-answer lists, feedback), and Model3D annotations; Diagram SVG and Simulation code render read-only in a subtle inset with the Regenerate control adjacent (FR-10, UX-DR7)
**And** `altText`/`longDescription` are editable as plain text wherever they exist (UX handoff item 15)
**And** the lesson-level `curriculumRef` is Teacher-correctable in review — editing it flips `source` to `"teacher"` (AD-2, UX handoff item 12; sign-off 2026-07-18).

**Given** any edit
**When** saved
**Then** the Draft revalidates against the schema package; validation errors pin inline to the offending field and the Draft does not persist non-conforming (FR-3, FR-10)
**And** edits preserve Citations as provenance-of-generation (OQ-10).

### Story 3.4: Autosave, Revision Concurrency, and Durability

As a Teacher,
I want no acknowledged edit ever lost — to expiry, conflict, or crash,
So that session mishaps never destroy review work.

**Acceptance Criteria:**

**Given** valid input in any editor field
**When** the Teacher pauses or blurs
**Then** autosave fires with a visible "Saved" state; failures show "Not saved — retrying" on the field plus a workspace banner, retaining edits locally — recovery is never silent (UX-DR8).

**Given** the Draft's optimistic `revision`
**When** a write carries a stale revision
**Then** the server returns 409 and the client performs the normative recovery: refetch, three-way per-Block rebase, true conflicts surfaced per Block — never wholesale discard, never blind replay (AD-23).

**Given** Authoring Session expiry with unsaved content (relaunch mints a fresh Launch Token, AD-14)
**When** the Teacher relaunches from Moodle
**Then** they land in the same Draft; locally preserved edits carry their base revision, and if the server has moved they stage as per-Block keep-mine/keep-server proposals — auto-replay forbidden (AD-23, UX-DR8)
**And** a session-ending warning banner precedes expiry when the lifetime is known.

**Given** the mandatory two-writer test floor
**When** the suite runs
**Then** regen-vs-edit, admin-vs-owner, and publish-vs-autosave scenarios all pass (AD-23).

### Story 3.5: Reorder, Delete, Discard, Whole-Lesson Regeneration, and the Block-Regeneration Framework

As a Teacher,
I want structural control of my Draft plus explicit regeneration paths,
So that I can shape a lesson or start fresh — always on my terms.

**Acceptance Criteria:**

**Given** the Block rail
**When** the Teacher reorders (drag or keyboard) or deletes a Block
**Then** the result revalidates as a conforming Draft; deletion visibly drops the Block's Citations (FR-10)
**And** Draft discard requires a destructive confirm and emits its Structured Event (A-28).

**Given** the "Regenerate entire lesson…" action
**When** invoked from the Workspace or Lesson card
**Then** the Generate form reopens prefilled (topic + guidance editable), the confirm names how many Blocks will be replaced, and submission explicitly re-runs the pipeline bypassing idempotency (FR-7, UX-DR4).

**Given** the Block-Regeneration framework (exercised by Diagram/Model3D/Simulation types in Epics 7/9/10)
**When** a single-Block regeneration runs
**Then** only that Block's stage re-runs and replaces it atomically with validations re-run; the job participates in the revision sequence and its completion notification carries `{block_id, new_revision}` so the editor rebases without a spurious 409; the rest of the Draft stays editable throughout; failure retains previous content with an error on that Block only (AD-17, AD-23, UX-DR19)
**And** Regeneration emits the `lesson_generated`/`generation_failed` family with `scope: block` (AD-7)
**And** the framework is verified in this story against a stub regenerable stage — its first real consumer is Story 7.2 (Diagram); Slide/Quiz/Narration are never regenerable (A-28).

### Story 3.6: Faithful Preview Overlay

As a Teacher,
I want to preview exactly what Students will see — including degraded states,
So that the Review Gate covers reality, not a flattering rendering.

**Acceptance Criteria:**

**Given** a Draft under review
**When** Preview opens
**Then** the real Player mounts against the current Draft (no separate preview renderer), with a no-op ResultsSink and `observer: true` so preview can never write results or consume attempts (FR-9, AD-10, AD-15).

**Given** the overlay controls
**When** used
**Then** device-width toggles (Phone 360 / Tablet 768 / Full) and the Low-spec view toggle (rendering exactly the Floor-tier states, with the honesty helper text) work; Simulation Blocks are interactive; Esc/Close returns with editor state intact; the overlay traps Tab and returns focus on close (A-27, UX-DR10).

### Story 3.7: Publish — Immutable Versions, Asset Freeze, Publish Dialog

As a Teacher,
I want publishing to be an explicit, checked, irreversible-by-design action,
So that Students only ever receive what I approved.

**Acceptance Criteria:**

**Given** a Draft and the publish action
**When** the publish job runs
**Then** its stages execute progress-visibly: revalidate → pre-publish checks → TTS stage (a no-op passthrough until Story 3.8 lands — sign-off 2026-07-18) → asset freeze into the immutable `lessons/{lesson_id}/v{n}/` prefix with `manifest.json` (hashes, sizes, licence metadata) → one final transaction asserting the checked `revision` is unchanged (AD-5, AD-9)
**And** publish requires `If-Match: revision`; a moved Draft yields `409 draft_changed_since_review` and the checks re-run (AD-23)
**And** the app DB role has no UPDATE/DELETE grant on `published_versions` — proven by a test attempting mutation (FR-11)
**And** the revalidate stage enforces that a Published Version contains **at least one block** — a publish-time invariant, deliberately NOT a schema rule: Drafts start empty by design (carried forward from the Story 1.1 review, stakeholder-recorded 2026-07-19).

**Given** the Publish dialog
**When** checks run
**Then** rows show pass/fail with per-Block readable reasons; any failure blocks publish with exits limited to Regenerate or delete that Block; success confirms explicitly, names the new version number, and points to Moodle placement (A-11, UX-DR11).

**Given** a republish
**When** complete
**Then** a new Published Version exists, prior versions remain stored and playable, new sessions receive the latest (FR-11, I-3), and `lesson_published` emits
**And** Student-facing surfaces can retrieve Published Versions only — no Student-accessible path to Drafts exists, and unpublished access yields the designed "not available" outcome (FR-12).

### Story 3.8: Publish-Time TTS Narration (AMD-1)

As a Teacher,
I want narration audio generated once at publish,
So that Students get voiced lessons at zero per-student cost.

**Acceptance Criteria:**

**Given** the publish job's TTS stage
**When** it runs
**Then** narration audio generates via the adapter's `tts` workload (speech surface) with full Cost Telemetry and governance, keyed by per-Block text hash so republish regenerates only changed audio (AD-3, AD-5)
**And** audio lands as static assets in the frozen version prefix, referenced by `audioRef`, included in the manifest — per-lesson cost, zero per-student cost (I-1).

**Given** `budgets.json` audio budgets (≤ 800 kB per Block, ≤ 10 MB per lesson)
**When** validators run at publish
**Then** over-budget audio fails the check with a per-Block reason (AD-11).

**Given** a TTS provider failure for some Blocks
**When** publish completes
**Then** the affected Narration Blocks publish without `audioRef` and the Player's fallback chain covers them — text is the always-available primary modality and audio is never promised universal `[ASSUMPTION: TTS failure degrades to publish-without-audio for the affected Blocks rather than blocking publish; the spine pins text-primary but not the failure posture — flag for confirmation]`
**And** the outcome is visible to the Teacher in the publish dialog and emits events.

## Epic 4: Player Core

A Student plays a Published Version end-to-end in the embeddable Player — degrading gracefully across capability tiers, scoring authoritatively, and never losing their place.

### Story 4.1: Embeddable IIFE Shell, Registries, and the Embedding Contract

As a Student,
I want the Player to mount cleanly inside any host page,
So that lessons feel native wherever they are embedded.

**Acceptance Criteria:**

**Given** the Player build
**When** produced
**Then** it is one self-contained IIFE exposing `EdonPlayer.mount(el, opts)`/`unmount`, syntax target ES2017/`chrome61` with the targeted polyfill set, no `import.meta.url` (base URL via `document.currentScript`), styles namespaced `edon-p-*` and container-scoped with no global resets (AD-11)
**And** CI enforces `budgets.json`: core ≤ 180 kB gzip hard fail; heavy renderers and polish as lazy chunks.

**Given** the Embedding Contract
**When** mounted in a host page
**Then** the Player inherits page scroll, fills container width fluidly, self-manages height (no nested scrollbars), reserves media boxes so load-ins never shift text, brings its own top edge into view on Block navigation, renders as an opaque bordered card, and leaves the browser back button to the host (UX-DR17).

**Given** the composition interfaces
**When** the shell boots
**Then** `BlockRegistry`, `LessonDeliverySource` (MVP `CompleteScriptSource`, async block-iterator signature), `NarrationProvider` registry, and `ResultsSink` are the only composition paths — each with its MVP implementation exercised on every play; unknown Block types are omitted from sequence and counts; no runtime schema validation runs in the Player (AD-10, FR-2).

### Story 4.2: Playback Bootstrap & Sessions

As a Student,
I want my session to arrive complete — script, attempt, resume, flags — in one shape,
So that playback state is never split across carriers.

**Acceptance Criteria:**

**Given** a mount with exactly `{scriptUrl, token, locale}`
**When** the Player's first act runs
**Then** `GET /api/v1/playback/bootstrap` (playback-token-authed) returns the pinned shape: script URL, attempt identifiers, `resume` (`open_attempt_id`, `position` as Block id, `viewed_block_ids[]`, per-Block `submissions`, `attempts_used`, `attempt_limit`), `feature_flags`, `governance_state`, `observer`, `tier_hints` (AD-22).

**Given** `observer: true` (preview, non-student roles)
**When** the session runs
**Then** the Player mounts the no-op sink and the platform refuses attempt creation and outbox rows (AD-15).

**Given** tenant feature flags
**When** playback renders
**Then** flags degrade presentation only (flag-off Simulation renders as Poster fallback); the server never strips Blocks from the script (AD-18)
**And** the dev-token path makes all of this testable before Moodle exists.

### Story 4.3: Slide Rendering, Navigation, and Progress Header

As a Student,
I want to step through slides with clear progress and instant text,
So that I always know where I am and never wait for words.

**Acceptance Criteria:**

**Given** a Published Version loading
**When** first paint happens
**Then** lesson title + first Slide text render before any heavy asset, in the system font stack, Slide text never behind a loader (UX-DR15); skeletons appear only for waits > 300 ms, resolve text-first, and are static below Showcase.

**Given** the shell chrome
**When** navigating
**Then** the "Block n of N" header + fill tracks position with a programmatic text equivalent; Back/Next are the only sequence navigation, always available (read-ahead allowed — completion, not navigation, requires quiz submission); on Block change focus moves to the new Block's heading (`tabindex="-1"`) and the live region announces "Block n of N — {title}" (UX-DR14, OQ-15)
**And** viewed marks report through the ResultsSink; Slide Blocks mark viewed on render
**And** touch targets ≥ 48 px; no swipe navigation; reading column ≤ 720 px.

### Story 4.4: Narration Providers & Transcript Floor

As a Student,
I want narration that plays when possible and reads as text always,
So that no device or voice situation excludes me.

**Acceptance Criteria:**

**Given** a Narration Block with `audioRef`
**When** the Student taps play
**Then** `PregeneratedAudioProvider` plays the static audio asset; without `audioRef`, `SpeechSynthesisProvider` is the fallback with voice preference following the script's language tag (en-NG → en-GB → any English) (AD-10, FR-14, AMD-1).

**Given** playback that does not audibly start within the bounded watchdog (3 s)
**When** the watchdog fires
**Then** the control quietly converts to the Floor state — transcript shown, play control hidden — never an error (UX-DR15)
**And** where no usable source exists at all, transcript shows by default (A-9).

**Given** the control bar
**When** used
**Then** narration never autoplays; "Show text" toggles the transcript exposing pressed/expanded state; transcript is real selectable text; narration state resets per Block (UX-DR15, UX-DR22).

### Story 4.5: Quiz Blocks — Instant Client Feedback

As a Student,
I want immediate feedback on every question,
So that I learn as I go instead of waiting for a grade.

**Acceptance Criteria:**

**Given** a Quiz Block with multiple-choice and short-answer questions
**When** the Student answers
**Then** feedback is instant and client-side with no server round-trip; short answers match deterministically (case/whitespace/punctuation normalised) against the Teacher-approved accepted-answer lists; no LLM judging exists (FR-15, OQ-4).

**Given** feedback rendering
**When** shown
**Then** it is announced via `role="status"` and programmatically associated with its question group; correctness pairs color with glyphs (✓/✗) and text; on an incorrect answer the correct option is marked with a check glyph and the "Correct answer" prefix; options are ≥ 48 px radio-group rows (UX-DR15, UX-DR22)
**And** answers shipping with the Published Version is the accepted formative-stakes trade-off (A-21) — the server score is what counts (Story 4.6).

### Story 4.6: Attempts, Server-Authoritative Scoring, Idempotent Submissions

As a Student,
I want my score recorded exactly once and authoritatively,
So that the gradebook entry is trustworthy no matter how flaky my network is.

**Acceptance Criteria:**

**Given** the attempt model
**When** a Student plays
**Then** an attempt = one Lesson run pinned to one Published Version, scoped `(lesson_id, activity_ref)`, consumed only at first Quiz submission (no-quiz lessons: unlimited runs); at bootstrap the Player declares the ordered Block ids its registry will render — the completion denominator — with omitted Blocks recorded for telemetry; server-side renderability inference is forbidden (AD-15).

**Given** a quiz submission
**When** it reaches the server
**Then** the server re-scores deterministically against the attempt's own Published Version; exactly one scored submission exists per (attempt_id, block_id) — idempotent on (attempt, block, uuid), a later different-uuid submission returns `409 already_submitted` with the recorded result; re-score + persistence + outbox rows commit in one transaction before ack; scores store as `earned/possible` fractions (FR-15, AD-15).

**Given** the submission UI
**When** the Student submits
**Then** Submit is single-fire (disabled on tap; a re-tap can never double-submit or double-consume); "Saving your score…" shows only after durable acceptance — until then "Don't close this page yet — still saving."; the localStorage outbox + `sendBeacon` retry persistent failures with "We'll keep saving your score — you can continue."; the client reconciles its outbox against `resume`'s per-Block submitted state before re-enabling any quiz (UX-DR15, A-13)
**And** a client-asserted score never reaches the gradebook record (OQ-14).

### Story 4.7: Resume, Completion Summary, and Sources

As a Student,
I want reload to restore my place and completion to be a clear picture,
So that interruptions — the normal case on my hardware — never cost me work.

**Acceptance Criteria:**

**Given** a mid-lesson reload (tab kill, battery saver, app switch)
**When** the Player re-bootstraps
**Then** it re-attaches to the open attempt without consuming a new one; viewed marks and submitted-quiz state visibly restore (or an honest designed state says what was kept) — never a silent restart at Block 1 (AD-15, UX-DR19).

**Given** completion
**When** all declared Blocks are viewed and all declared Quiz Blocks submitted
**Then** the completion summary renders: tick list, server-score status, attempts line (falling back to last-known or "—", never a spinner), jump-back links for anything missing, and the cross-version "Your best score so far: X" line on retakes that landed on a newer version (OQ-15, UX-DR14)
**And** retake is explicit, post-completion, loads the latest version; in-flight sessions keep their pinned version with the one-line "Your lecturer updated this lesson." on version change (A-4).

**Given** the lesson end
**When** rendered
**Then** the collapsed Sources section lists Lesson-level Citations — per-Block display is Teacher-only (OQ-10).

### Story 4.8: Capability Tiers & Degradation Framework

As a Student on any device,
I want the lesson to adapt to my hardware and data situation gracefully,
So that it completes everywhere — polished where possible, honest where not.

**Acceptance Criteria:**

**Given** feature-based detection (never user-agent)
**When** the Player classifies the session
**Then** Showcase/Full/Constrained/Floor resolve per the ladder with demote-when-unsure; any data-saver signal (`saveData`, `prefers-reduced-data`, metered hints) switches heavy assets from auto-load (the default everywhere) to tap-to-load with transfer-size labels from `transferSize` (AD-11, UX-DR16).

**Given** heavy Blocks
**When** the Student moves through the lesson
**Then** at most one heavy Block is live at a time; leaving releases it to poster; returning re-loads from cache without re-prompting (size label reappears only if re-download is real); posters are budgeted, lazy, and derived from content (UX-DR16)
**And** the Poster fallback card renders as first-class content (poster + caption + annotations/parameters as text), counts as viewed, and completion is tier-independent — the Floor reaches 100% (FR-18).

**Given** the Constrained predicate (`deviceMemory ≤ 2` or undefined → halved asset ceiling; any load failure/timeout → Constrained behavior)
**When** triggered
**Then** the fallback mechanics engage without error styling (AD-11).

### Story 4.9: Defined Failure & Edge States

As a Student,
I want every failure to land on a designed state,
So that nothing in a lesson ever looks broken or blames me.

**Acceptance Criteria:**

**Given** the edge-state catalogue
**When** each condition occurs
**Then** the Player renders its designed state: unknown Block types omitted from sequence and counts entirely (no gap card); major-version mismatch and zero-renderable-Blocks → the calm can't-play state; bundle/script fetch failure → "This lesson couldn't load. Try again." with retry, never a blank region; mid-lesson connectivity loss → current Block usable, inline retry on Next without position reset; unpublished lesson → "This lesson isn't available yet. Ask your lecturer." (FR-2, FR-12, UX-DR19).

**Given** attempts exhausted
**When** the Student returns
**Then** answers are reviewable read-only with the attempts-used line; the highest attempt stands (OQ-15).

**Given** the CI fixture corpus
**When** Player tests run
**Then** the unknown-block and future-version fixtures play per FR-2 — proving forward compatibility at the Player.

## Epic 5: Platform LMS Edge

The platform speaks its LMS-agnostic integration surface — everything mod_edonlesson needs, with Moodle knowledge confined entirely to the plugin.

### Story 5.1: Launch Token Verification & Authoring Sessions

As a Teacher,
I want my Moodle launch to become a secure Authoring session,
So that I never manage a separate login.

**Acceptance Criteria:**

**Given** a Launch Token minted by the plugin (Epic 6) or the dev CLI
**When** presented on the launch endpoint
**Then** the platform verifies HS256 against the per-tenant secret, the 120 s lifetime, and single-use `jti` (fragment transport), then issues the Authoring Session cookie (HttpOnly, 8 h absolute) bound to tenant, user, role, and course reference (FR-29, AD-14).

**Given** an expired, replayed, or tampered token
**When** presented
**Then** the outcome is the Relaunch notice — one sentence, no login form, no retry, never partial access (FR-29, UX-DR8)
**And** a relaunch lands the Teacher in the same Draft they were editing (AD-23).

**Given** the session near expiry
**When** T-15 min is reached
**Then** the session surface exposes the warning data the Authoring UI's banner consumes (UX-DR8)
**And** the platform never enumerates Moodle courses — the course reference on every Generation Job equals the token's (FR-4).

### Story 5.2: Tenant Server-to-Server Auth, Key Rotation, and CORS

As the Operator,
I want each Moodle instance authenticated per tenant with rotatable keys and pinned origins,
So that integration credentials stay hygienic for ~60 colleges.

**Acceptance Criteria:**

**Given** the integration endpoints
**When** called
**Then** `Authorization: Bearer` with a tenant API key resolves the TenantContext; keys are hashed, two concurrently valid, and rotate without downtime (issue new → cut over → revoke old, proven by test) (FR-24, NFR-3).

**Given** CORS configuration
**When** a browser origin calls tenant-scoped endpoints
**Then** only that tenant's configured origins are allowed — no wildcard anywhere ([HARD] §4)
**And** auth failures emit audited structured events with tenant attribution where resolvable.

### Story 5.3: Lesson Picker & Playback Session APIs

As a Teacher,
I want the plugin to list my college's published lessons and open Student sessions,
So that activity placement and playback work end to end.

**Acceptance Criteria:**

**Given** the picker endpoint
**When** the plugin requests it for a course
**Then** it returns the tenant's Published Versions (lesson title, version, curriculum reference) with `limit` + opaque `cursor` pagination — LMS-agnostic nouns only, `lms_user_id` as an opaque string (AD-16, FR-22).

**Given** a Student launching an activity
**When** the plugin requests a playback session
**Then** the platform issues the lesson+attempt-scoped playback token and the session response the plugin needs; that response is for the plugin's own display only and is never re-serialized into the page — everything the Player needs arrives via bootstrap (AD-22).

### Story 5.4: Delivery Outbox — Pull and Ack

As the platform,
I want grades and completions delivered via pull-and-ack,
So that no inbound connection couples us to institutional hosting and no writeback is ever lost.

**Acceptance Criteria:**

**Given** outbox rows created transactionally with attempts (Story 4.6)
**When** the plugin's scheduled task pulls
**Then** pending deliveries return paginated per tenant; each ack is `applied | failed {error_code}`; a failed ack emits `writeback_failure`, redelivery on the next run emits `writeback_retry`, and redelivery is idempotent on the plugin side by delivery id (AD-16, FR-23).

**Given** rows aging past the SM-3 window (24 h, config)
**When** the maintenance sweep runs
**Then** `writeback_overdue` emits per affected row — the weekly-ops signal (AD-16, A-25).

### Story 5.5: Integration Contracts Frozen

As the team,
I want the three external contracts versioned and pinned by tests,
So that changes to what we need from external systems are explicit work items, never drift.

**Acceptance Criteria:**

**Given** `/docs/integrations`
**When** this story completes
**Then** `edon-rag-retrieval.md` (v1.2), `mod-edonlesson-platform-api.md` (launch, picker, sessions, bootstrap, outbox pull/ack shapes), and `block-edon-ai-diagram-api.md` (diagram request/response with rendered `message` strings) are current and versioned (AR-27)
**And** contract tests pin every documented shape so an accidental change fails CI
**And** the docs state the change rule: contract changes are work items, never assumed edits to external systems (project-context §8).

## Epic 6: mod_edonlesson Companion Plugin (companion repo, GPLv3)

A Teacher places Published Versions in courses and launches authoring from Moodle; Students play embedded lessons whose grades and completion land in the gradebook — the thin plugin.

### Story 6.1: Plugin Scaffold & Tenant Configuration

As a Moodle administrator,
I want the activity module installable and configured with my college's credentials,
So that our Moodle connects to the platform securely.

**Acceptance Criteria:**

**Given** the separate `mod_edonlesson` repository
**When** the plugin installs on Moodle 5.x
**Then** it is a standard activity module, GPLv3, containing no proprietary platform logic — a thin client of the platform API (FR-22, NFR-7)
**And** admin settings hold the platform base URL and tenant API key; all rendered surfaces use standard Moodle renderers/output APIs, theme-inherited with zero per-school customization (WI-MOD-0).

**Given** Moodle plugin hygiene requirements
**When** reviewed
**Then** the privacy provider declares what the plugin stores, and backup/restore support covers activity instances `[ASSUMPTION: Moodle privacy + backup APIs are required plugin-compliance hygiene, folded here rather than a separate story]`.

### Story 6.2: Activity Creation via the Lesson Picker

As a Teacher,
I want to add a lesson activity by picking a Published Version,
So that placement needs normal course-editing rights and nothing else.

**Acceptance Criteria:**

**Given** "Add an activity" → e-DON Lesson
**When** the Teacher configures the activity
**Then** the picker lists the college's Published Versions via Story 5.3, and completion options plus quiz attempt limits are configured here — in Moodle settings, as teachers expect from other modules (FR-22, OQ-15, UX-DR21)
**And** the activity stores the lesson reference; a Teacher with normal course-editing rights completes placement with no platform-side help (FR-22).

### Story 6.3: Embedded Playback with Production-Theme Style Isolation (M3 gate item)

As a Student,
I want the lesson playing inside my activity page,
So that learning never leaves my course.

**Acceptance Criteria:**

**Given** a Student opening the activity in a browser
**When** the page renders
**Then** the plugin embeds the Player with exactly `EdonPlayer.mount(el, {scriptUrl, token, locale})` after obtaining the playback session — no redirect, one instance per page, browser back stays Moodle's (FR-22, AD-22).

**Given** the production (Almondb-based) theme on staging Moodle
**When** the embed is inspected
**Then** style isolation is verified both directions — no Player style bleeds into Moodle, no theme style breaks the Player card — and the verification is recorded as M3 gate evidence (spine M3, UX-DR17).

**Given** the Moodle mobile app
**When** a Student opens the activity
**Then** the designed hand-off renders — "This lesson opens in your browser." with one button — never an unstyled fallback (UX-DR17).

### Story 6.4: Completion & Gradebook Writeback Scheduled Task

As a Teacher,
I want scores and completion in the gradebook I already use, automatically,
So that results flow without manual transfer.

**Acceptance Criteria:**

**Given** the plugin's scheduled task
**When** it runs
**Then** it drains the platform outbox (pull + ack per Story 5.4), writes grades via gradelib (grade = max fraction × grademax) attributed to the correct Moodle user, and updates completion state per the activity's completion options (FR-23, AD-16)
**And** application is idempotent by delivery id — a redelivered row never double-writes.

**Given** a full staging pass
**When** a Student completes a lesson with a quiz
**Then** the grade and completion appear in the course gradebook and course page tick within the SM-3 window, with writeback failures logged and retried without Student rework (SM-3, A-13).

### Story 6.5: Teacher Entry Point — Launch Token Minting

As a Teacher,
I want "Open Lesson Studio" one click from my course,
So that authoring starts where I already work.

**Acceptance Criteria:**

**Given** the activity's teacher view
**When** a user with teacher capability clicks "Open Lesson Studio"
**Then** the plugin mints the Launch Token (HS256, per-tenant secret, tenant + user + role + course reference, 120 s, unique `jti`) and opens the Authoring UI in a new tab with fragment transport (FR-29, AD-14, UX handoff)
**And** the platform accepts it exactly once (Story 5.1); Students never see the entry point
**And** from the Moodle app, the entry point opens the system browser (UX-DR17).

## Epic 7: Diagram Blocks & the Governed Student Diagram Channel

Lessons gain reviewed Diagram Blocks; Students gain on-demand labelled diagrams in chat — the one Review-Gate bypass fully inside its governance loop.

### Story 7.1: The Sanitisation Gate

As the platform,
I want one server-side allowlist sanitiser as the only path to storage,
So that unsanitised SVG can never reach a renderer — while accessibility survives the pass.

**Acceptance Criteria:**

**Given** any LLM-derived SVG (direct or via an intermediate representation, Teacher- or Student-side)
**When** it heads for storage
**Then** the single server-side sanitiser (defusedxml-parsed, tag + attribute allowlist) strips scripts, event handlers, `foreignObject`, and external references; what cannot be made conforming is rejected outright — Mermaid or any intermediate grants no exemption (FR-20, AD-13)
**And** the allowlist explicitly preserves `<title>`, `<desc>`, `role="img"`, `aria-label`, `aria-labelledby` (UX handoff item 15).

**Given** the same pass
**When** it runs
**Then** the diagram label-legibility check executes (font-size/viewBox math at 360 px) and fails illegible diagrams (AD-13)
**And** a sanitisation failure produces the clear "couldn't produce that diagram" outcome plus a Structured Event — never partial unsanitised content (FR-20).

**Given** the [HARD]-rule protection requirement
**When** the suite runs
**Then** sanitiser unit tests cover the allowlist, the rejection path, and the accessibility-preservation list (project-context §7); client-side DOMPurify (SVG profile) runs at render as defense-in-depth only, never the gate.

### Story 7.2: Diagram Blocks in Lessons

As a Teacher,
I want generated labelled diagrams in my lessons,
So that visual content is grounded, reviewed, and accurate.

**Acceptance Criteria:**

**Given** the `diagram_generation` pipeline stage (mini-tier model with structured output, per workload config)
**When** it produces a Diagram Block
**Then** the SVG passes the sanitisation gate before the Draft persists, carries populated `altText`/`longDescription` from the same Grounding Chunks, respects the ≤ 200 kB budget, and stores its Citations (FR-20, UX handoff 15, AD-11).

**Given** the Player's Diagram Block renderer
**When** a Student views it
**Then** the reviewed SVG scales to container width with the "View larger" affordance (a link, not an overlay), the text alternative is exposed, and no AI label appears — this content passed the Review Gate (UX-DR15).

**Given** the Block-Regeneration framework (Story 3.5)
**When** a Teacher regenerates a Diagram Block
**Then** only that Block re-runs (stage + sanitisation + legibility), replacing atomically with Citations updated (FR-10).

### Story 7.3: Student Diagram Endpoint — Cache → Governance → Generate → Sanitise

As a Student,
I want to request a labelled diagram and get it fast, grounded, and safe,
So that visual help arrives inside the chat I already use.

**Acceptance Criteria:**

**Given** a Diagram Request
**When** the platform endpoint processes it
**Then** the AD-21 flow runs in order: normalise via the shared `normalise_key` → tenant-scoped cache lookup — a hit returns instantly, emits `diagram_served_from_cache` plus a zero-cost telemetry row, and never charges the Rate Limit — → on miss: governance pre-flight → identity-stripped tenant-scoped retrieval + mini-tier structured generation → sanitisation gate → store (cache key `sha256(normalised_text)` hex) and serve (FR-19, FR-21, AD-21).

**Given** the served diagram
**When** rendered by the client contract
**Then** it carries the verbatim FR-28 label and its generated description/`altText`; no Student personal identifier appeared in any prompt or provider request (NFR-9)
**And** `diagram_requested` and related events emit with tenant + pseudonym attribution (FR-27).

### Story 7.4: Diagram Limits & Humane Messaging

As a Student,
I want limits explained plainly, with when-I-can-retry,
So that cost control never feels like a wall or a scolding.

**Acceptance Criteria:**

**Given** the governance policies
**When** a Student exceeds the per-Student Rate Limit (temporal) or the daily diagram Quota (countable, default 20/Student/day, tenant config), or the tenant enters budget cache-only mode
**Then** each state returns its distinct, humane, fully rendered `message` string (AD-20 split: the chat client stays dumb), with every number and window interpolated from tenant config — exemplar copy per EXPERIENCE.md (FR-21, FR-26, UX-DR18)
**And** cache hits still serve normally in cache-only mode (OQ-9).

**Given** denial events
**When** emitted
**Then** Rate Limit/Quota rejections are Structured Events sufficient to compute SM-C3 (denial rate) from stored data alone (FR-27).

### Story 7.5: Report Control & Review Queue (Backend)

As a Student,
I want to flag a doubtful diagram for my lecturer,
So that the Review-Gate bypass has a human backstop.

**Acceptance Criteria:**

**Given** a served diagram
**When** the Student reports it
**Then** the report endpoint enqueues a review-queue row with the pinned shape `{diagram_id, raw_request_text, normalised_text, svg_asset_ref, report_count, latest_note, requested_at}`, aggregates repeat reports into `report_count`, stores `diagram_id → cache_key`, and emits `diagram_reported` (FR-28, AD-21).

**Given** the queue list endpoint
**When** the Authoring UI requests it
**Then** rows return tenant-scoped with limit/cursor pagination
**And** telemetry-sampled spot checks require no additional surface — diagram events + Cost Telemetry suffice by design (FR-28).

### Story 7.6: Diagram Review Queue UI & Invalidation

As a Teacher,
I want to triage reported diagrams and evict bad ones permanently,
So that the governance loop closes inside tools I already have.

**Acceptance Criteria:**

**Given** the Diagram review queue surface (Course home header nav, count badge when non-empty)
**When** the Teacher opens it
**Then** rows show thumbnail, original request text, report count, and date; the branded empty state covers the quiet case (UX-DR13).

**Given** a queue row
**When** the Teacher acts
**Then** "Mark reviewed" clears the row and emits `diagram_review_completed`; "Mark invalid" (destructive confirm) clears the row, **deletes the tenant cache entry**, and emits `diagram_invalidated` — that diagram is never served again and the next equivalent request regenerates fresh; both actions are core use-cases (AD-21, AD-7)
**And** the loop — label → report → review → removal — is demonstrable end to end (Flow 5, M4 gate).

## Epic 8: block_edon_ai Companion Enhancement (companion repo)

The existing chat renders the diagram experience with a minimal surface and embeds course-scoped on the lesson activity page — Live Q&A beside every lesson.

### Story 8.1: Diagram Chat Message Component

As a Student,
I want the diagram experience inside the chat I already use,
So that there is no new tool to learn.

**Acceptance Criteria:**

**Given** the block_edon_ai chat
**When** a Student requests a diagram
**Then** the message flow renders: request → "Drawing your diagram… this can take a moment." → the sanitised SVG card — the block calls the platform diagram endpoint and renders what returns; Sanitisation, caching, Quotas, and identity-stripping all remain server-side (minimal surface, OQ-12)
**And** the chat's own chrome is untouched; only the diagram message is specified (UX-DR20).

**Given** a cache hit
**When** rendered
**Then** it appears instantly and visually identical to a fresh diagram, label included (FR-21)
**And** message states announce via the chat's live region; the diagram card's accessible name is the AI label + the Student's request text + the generated description (UX-DR22).

### Story 8.2: AI Label & Report Control

As a Student,
I want the provenance label always visible and reporting one tap away,
So that trust signals are unmissable on the one unreviewed channel.

**Acceptance Criteria:**

**Given** every rendered chat diagram
**When** displayed
**Then** the verbatim label "AI-generated — verify against your course materials" is pinned, never dismissible, never truncated, never reworded, in the gold-wash + accent-ink treatment (FR-28, UX-DR1)
**And** "Report this diagram" renders at ≥ 48 px hit area (Player/chat floor, UX-DR22 — ratified at sign-off 2026-07-18); on tap it calls the report endpoint, confirms with "Thanks — your lecturer will review this diagram.", and disables for that diagram (FR-28, UX-DR20).

### Story 8.3: WI-CHAT-4 — Course-Scoped Chat on the Lesson Activity Page (AMD-2)

As a Student,
I want the course chat available beside my lesson,
So that live Q&A accompanies learning without new economics.

**Acceptance Criteria:**

**Given** a lesson activity page
**When** it renders for a Student
**Then** the existing block_edon_ai chat is presented with the activity, scoped to the launch course — no new inference economics, NFR-9 identity-stripping unchanged (AMD-2)
**And** the embed respects the Player's Embedding Contract (no scroll traps, no layout interference) and degrades gracefully to the plain activity page when the block is unavailable `[ASSUMPTION: graceful absence rather than a hard dependency — the lesson must remain fully usable without the chat]`.

### Story 8.4: Limit States & Feature Flag-Off in Chat

As a Student,
I want limits and failures as plain chat replies,
So that the chat never errors technically at me.

**Acceptance Criteria:**

**Given** the platform's rendered message strings (Story 7.4)
**When** a Rate Limit, daily Quota, budget cache-only, or sanitisation/generation failure occurs
**Then** each renders as a chat reply in Voice-and-Tone copy with tenant-config-interpolated values — the chat never shows a technical error (UX-DR20)
**And** when `feature.diagrams` is off for the tenant, no diagram affordance appears and the chat behaves exactly as today (FR-26).

## Epic 9: Model3D Blocks & the Curated Library (BLOCKED until OQ-6 seed bar met)

Teachers get lessons with interactive, annotated, licence-attributed 3D models; the library gets its ingest pipeline and its stakeholder-curated seed. **No story in this epic starts before the ≥ 20-model curated seed library exists (OQ-6; stakeholder is the curator) — except 9.1, which builds the ingest tooling the curation itself needs** `[ASSUMPTION: the ingest CLI must precede the seed intake it enables; the OQ-6 block is read as gating Model3D lesson features (9.2–9.4), not the tooling]`.

### Story 9.1: Model Ingest Pipeline & Library Registry

As the Operator (curator),
I want a CLI that normalises, compresses, budgets, posters, and licence-checks every model,
So that only compliant assets can enter the library.

**Acceptance Criteria:**

**Given** a candidate glTF asset
**When** ingested via the CLI (gltf-transform)
**Then** it is Draco-compressed, its `transferSize` computed, and validated against `budgets.json` (≤ 10 MB transfer hard cap, ≤ 6 MB preferred at selection); a poster is captured deterministically from the glTF viewer at ingest (AD-17, AD-11)
**And** ingest **rejects** any asset without licence and attribution metadata; only openly licensed assets enter ([HARD] §5, FR-16).

**Given** the library registry
**When** assets land
**Then** `MODEL_ASSET` records carry licence, attribution, curriculum-mapping fields, poster ref, and sizes `[ASSUMPTION: platform-global library with tenant visibility rules, per the spine's either-is-safe note — final call at migration time]`.

### Story 9.2: Seed Library Intake (EXTERNAL INPUT: stakeholder-curated, ≥ 20 models — the M5 gate blocker)

As a Teacher,
I want a curriculum-mapped model library covering my science subjects,
So that generation has real, relevant assets to select.

**Acceptance Criteria:**

**Given** the stakeholder-curated candidate set (curation itself is the stakeholder's deliverable, not this story's)
**When** intake completes
**Then** ≥ 20 models are ingested via Story 9.1 across 2–3 NCE science subjects, each with verified open licence + attribution metadata and curriculum tags (OQ-6)
**And** the count and coverage are recorded as M5 gate evidence — Model3D lesson stories and the M5 gate remain blocked until this bar is met.

### Story 9.3: Pipeline Model3D Selection Stage

As a Teacher,
I want generation to select and configure models — never invent geometry,
So that 3D content is accurate, licensed, and safe.

**Acceptance Criteria:**

**Given** the generation pipeline with the library seeded
**When** a topic warrants a Model3D Block
**Then** the stage selects from the Curated Model Library by curriculum mapping, authors annotations into the Lesson Script, populates `altText` and the poster reference, and stores Citations; no pipeline path creates 3D geometry (FR-16)
**And** the Block-Regeneration framework re-runs selection/configuration for that Block only (FR-10).

### Story 9.4: Model3D Viewer Renderer

As a Student,
I want an interactive, annotated 3D viewer,
So that I can explore structures hands-on — or read them when my device can't.

**Acceptance Criteria:**

**Given** a Model3D Block on a capable tier
**When** it loads (auto-load default; tap-to-load with size label under data-saver)
**Then** the lazy `model3d` chunk (≤ 250 kB gzip, Three.js) renders the glTF with poster as instant first paint; orbit (drag or arrow keys — focusable canvas with role and name) and zoom work; the control row (rotate, zoom ±, reset, annotations toggle) duplicates every gesture; gestures capture only after the asset is interactive (FR-16, UX-DR15)
**And** annotation markers and the toggle open the annotation text panel on every tier; the attribution/licence line renders from asset metadata (FR-16).

**Given** Constrained/Floor conditions or any load failure
**When** the Block renders
**Then** the Poster fallback card shows with annotations as a text list, counts as viewed, and the lesson completes (FR-18)
**And** the hero entrance ships later in the Showcase chunk (Epic 11) — this story's viewer is entrance-free by design.

## Epic 10: Simulation Blocks, Template-First

Students manipulate parameter-driven simulations that ran the gauntlet: locked sandbox, pinned protocol, headless checks, template library as launch mode.

### Story 10.1: Sandbox Runtime & postMessage Protocol v1

As the platform,
I want the locked sandbox and pinned protocol,
So that simulations can never escape and both modes speak one language.

**Acceptance Criteria:**

**Given** a Simulation Block frame
**When** it runs
**Then** the iframe uses `sandbox="allow-scripts"` (never `allow-same-origin`) with srcdoc-injected CSP `default-src 'none'`; no network, storage, or parent-frame access exists beyond the protocol — proven by escape-attempt tests (FR-17 [HARD], AD-12).

**Given** protocol v1 documented in `/schema`
**When** implemented
**Then** the message set (`sim:hello/host:init/sim:ready/sim:state/sim:error/host:set-param`), the param descriptor array (`[{id, label, type, min, max, step, default}]`), the mandatory `sim:state` echo after `host:set-param`, and the `data-edon-param` DOM markers are all pinned; a 10 s readiness watchdog lands on the poster fallback (AD-12)
**And** template guidelines and generation prompts derive from that document — never the reverse.

### Story 10.2: Pre-Publish Check Harness

As a Teacher,
I want automated checks gating publish,
So that a broken simulation can never reach Students.

**Acceptance Criteria:**

**Given** a Draft containing a Simulation Block
**When** the pre-publish checks run (headless Chromium, server-side)
**Then** they verify: loads without runtime error; `sim:ready` within time; declared parameters present **and keyboard-operable via native controls** (the `data-edon-param` assertion); responds to `host:set-param` with the `sim:state` echo; resource budget respected (≤ 1.5 MB, heap ≤ 128 MB, no > 1 s main-thread task) (A-35 extended, AD-12, UX-DR22)
**And** any failure blocks publish with the per-Block readable reason in the Publish dialog — exits are Regenerate or delete (A-11, wired into Story 3.7)
**And** the same checks run on Block Regeneration of a Simulation (FR-10).

### Story 10.3: Simulation Template Seed Set (first-class deliverable)

As a Teacher,
I want a library of parameterised simulation templates,
So that launch simulations are reliable by construction.

**Acceptance Criteria:**

**Given** the `SIM_TEMPLATE` registry
**When** the seed set lands
**Then** templates cover NCE science topics with declared parameter descriptors, and every template passes the Story 10.2 checks and protocol conformance `[ASSUMPTION: seed count/topic coverage set with the stakeholder at story kickoff — the artifacts pin the deliverable's first-class status (OQ-5) but no numeric bar]`
**And** template guidelines (derived from the protocol document) are recorded so future templates stay conformant.

### Story 10.4: Pipeline Simulation Stage (Template Mode)

As a Teacher,
I want generation to configure a template for my topic,
So that simulations arrive grounded and safe — the launch default regardless of benchmark outcome.

**Acceptance Criteria:**

**Given** the `simulation_generation` workload
**When** the stage runs
**Then** it selects and parameterises a template (`mode: "template"`, `templateId` + params per schema), grounded in Grounding Chunks with Citations stored; the poster's `altText`/`longDescription` populate from the same Grounding Chunks (text-alternative contract, UX handoff item 15); the Block passes the Story 10.2 checks at generation time and again at publish (OQ-5, FR-17)
**And** the poster derives from a headless capture at `sim:ready` (deterministic, AD-17); Block-Regeneration re-runs this stage per the framework (FR-10).

### Story 10.5: Player Simulation Frame

As a Student,
I want to run simulations and manipulate parameters live,
So that I learn by experiment on my own device.

**Acceptance Criteria:**

**Given** a Simulation Block on a capable tier
**When** it renders (auto-load default; tap-to-load "Run simulation (size)" under data-saver)
**Then** the poster is first paint, the sandboxed iframe starts, and manipulating an authored parameter changes the simulation live via the protocol; the `simulation` chunk stays ≤ 60 kB (FR-17, AD-11)
**And** sound/narration start only on explicit action; the frame carries an accessible title.

**Given** a load failure, crash, or missed readiness within the bounded wait
**When** detected (a hard-crashed sandbox emits nothing — the bounded wait is the mechanism)
**Then** the Poster fallback card renders with parameter descriptions as text — quiet on the page, honest in the caption, counting as viewed (UX-DR15, FR-18)
**And** Simulation interaction works in the Teacher Preview overlay (FR-9); flag-off tenants see Published Simulation Blocks as poster cards (AD-18).

### Story 10.6: Freecode Dual-Mode Support (flagged; activation excluded from scope)

As the platform,
I want freecode simulations supported behind the tenant flag,
So that the OQ-5 ship choice stays configuration — not a schema fork.

**Acceptance Criteria:**

**Given** the schema's dual mode
**When** a `mode: "freecode"` Block with `bundleRef` is processed
**Then** it flows through the identical sandbox, protocol, and check harness — no second path (AD-12)
**And** the pipeline's freecode stage exists behind `feature.simulation_freecode` `[ASSUMPTION: flag name follows the AD-18 pattern]`, default off for every tenant.

**Given** the activation criteria (ADR-002's ≥ 70% automated-check pass gate)
**When** this story completes
**Then** the criteria are documented as a stakeholder-owned activation decision — no story, epic, or gate blocks on it (AR-30, OQ-5).

## Epic 11: Showcase Polish & Launch Hardening

The canonical Showcase experience lands inside enforced budgets, and the platform proves launch-ready for the ≤ 5-college sponsored pilot.

### Story 11.1: Showcase Enhancement Chunks — Fonts & Motion

As a Student on a modern phone,
I want the flagship polished experience,
So that the product feels world-class — without ever costing the floor.

**Acceptance Criteria:**

**Given** the lazy `fonts+motion` chunk (≤ 300 kB gzip, post-first-paint, never render-blocking, never counted against core)
**When** it lands on capable devices
**Then** Player text upgrades to Inter + Plus Jakarta Sans as standard (system stack remains the fallback at every moment), and the Showcase motion language activates: ≤ 300 ms Block transitions, shimmer skeletons, stepped-to-smooth progress (AD-11, UX-DR2, UX-DR23).

**Given** the signature moments
**When** they play
**Then** the Model3D hero entrance (fade-in + slow ~2 s auto-orbit, settling, entirely inside the reserved media box) and the quiz-success celebration (green-family check-draw + wash pulse, ≤ 600 ms, once per question, never gold, copy stays plain) render on Showcase only (UX-DR23)
**And** every animation suppresses under `prefers-reduced-motion`, no motion ever touches gold governance elements, and tiers below Showcase stay static (DESIGN.md).

### Story 11.2: Performance Gates in CI

As the team,
I want the blocking modern-profile check and the advisory low-spec profile,
So that perceived performance is enforced where it gates and informative where it doesn't.

**Acceptance Criteria:**

**Given** the CI performance suite
**When** it runs
**Then** the **blocking** check passes on the standard modern profile (unthrottled Chromium, 4G-shaped network): lesson title + first Slide text ≤ 2.5 s; the throttled low-spec profile (CPU 6×, 400 kbps/400 ms RTT, ~1.5 GB memory cap) runs and reports **advisory**, not gating (AD-11, NFR-2)
**And** every `budgets.json` value is enforced by its consumer (player CI, pipeline validators, ingest CLI, simulation harness) — no second budget source exists
**And** the old-engine smoke test passes (ES2017/`chrome61` floor).

### Story 11.3: i18n & Copy Completeness Audit

As the team,
I want every user-facing string externalised and voice-compliant,
So that localisation stays a roadmap-cheap catalog swap.

**Acceptance Criteria:**

**Given** all surfaces (Authoring, Player chrome, chat card copy, platform-emitted messages)
**When** the audit runs
**Then** the i18n lint gate is clean; the `en` catalog is complete under `surface.component.slug` keys; every limit/quota copy interpolates tenant config values (no hardcoded numbers anywhere); the FR-28 label is byte-exact everywhere it appears (AD-20, NFR-8, UX-DR18)
**And** Lesson Script language tags flow to Player content regions and diagram cards as `lang` attributes (UX-DR22).

### Story 11.4: Accessibility AA Audit

As the team,
I want the scoped WCAG 2.1 AA target verified end to end,
So that the accessibility floor is demonstrated, not asserted.

**Acceptance Criteria:**

**Given** the OQ-7 scope (full AA on controlled surfaces: Authoring UI, Player chrome, designed states, Moodle-native surfaces; text-alternative contract + best-effort on AI content)
**When** the audit runs across all three surfaces
**Then** keyboard operability (incl. Simulation params via the check harness), focus indicators, target sizes (≥ 48 px Player/chat, ≥ 44 px authoring), contrast pairs per DESIGN.md § Colors, `aria-live` behavior, toggle state exposure, and the policy-disabled-control/banner association all verify (UX-DR22)
**And** the text-alternative contract is proven end to end: pipeline populates → Teacher edits → Player/chat exposes (UX handoff 15)
**And** findings are fixed or explicitly waived by the stakeholder — no silent gaps.

### Story 11.5: Ops — Monitoring, Runbooks, Weekly Checklist

As the Operator,
I want alerting and runbooks in place,
So that the pilot runs on discipline, not heroics.

**Acceptance Criteria:**

**Given** the ops tooling milestone
**When** complete
**Then** alerting beyond journald covers uptime, disk, `writeback_overdue`, and `cost_alert` `[ASSUMPTION: alert transport (email/webhook) is an ops choice made in-story — the spine defers it to this epic]`
**And** runbooks exist and are exercised: deploy, backup/restore (drill actually executed against staging), key rotation (tenant + operator), tenant onboarding
**And** the one-page **weekly ops checklist** (spend alerts, `writeback_overdue` review, diagram-report queue, key rotations) is delivered and run once for real — the M6 gate demonstration (AR-28).

### Story 11.6: Pilot-Readiness Verification

As the stakeholder,
I want the launch posture proven,
So that ≤ 5 colleges onboard onto a system whose claims are all demonstrated.

**Acceptance Criteria:**

**Given** stored platform data alone
**When** the metric queries run
**Then** SM-1..SM-5, SM-C1..SM-C3, and the OQ-18 adoption metric (% of Published lessons with ≥ 1 Student completion within 30 days) all compute — no missing instrumentation (FR-27, AD-19)
**And** the replay path is verified to contain zero LLM calls (SM-4's structural claim), the retention job is verified live, and the processor record is current (NFR-9).

**Given** the staging environment
**When** the final pass runs
**Then** the golden-path pipeline is green on recorded fixtures, the live smoke tenant exercises WI-RAG-0's endpoint (or its absence is explicitly re-gated with the stakeholder), and the M6 preview demonstration completes against the gate's exit criteria
**And** launch configuration (per-workload models per ADR-002's current addenda, tenant policies, budgets) is reviewed and recorded — launch-ready.
