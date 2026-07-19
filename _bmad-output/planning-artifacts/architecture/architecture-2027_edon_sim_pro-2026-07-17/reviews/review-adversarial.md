# Adversarial Review — ARCHITECTURE-SPINE (e-DON Lesson Studio)

**Lens:** adversarial reviewer gate — construct units one level down that each obey every AD to the letter yet build incompatibly.
**Artifact:** `ARCHITECTURE-SPINE.md` (AD-1..AD-21 + conventions), run 2026-07-17.
**Context consumed:** ADR-001..ADR-014, `docs/integrations/*.md` (all three).
**Units (epics) attacked pairwise:** SCHEMA (schema package) · PIPELINE (generation) · AUTHORING (review/publish) · PLAYER · DIAGRAM · MOODLE (plugin + platform integration API) · GOVOPS (tenancy/governance/ops).

**Verdict: REVISE BEFORE EPIC HAND-OFF.** The ADs are individually sound and unusually well-fenced, but 21 letter-compliant divergence constructions exist across epic seams — 3 critical, 8 high. Every one closes with a tightened or new AD; none requires redesign.

| Tier | Count |
| --- | --- |
| Critical | 3 |
| High | 8 |
| Medium | 7 |
| Low | 3 |

Method note: each scenario below shows (a) the two units and the contract they share, (b) a construction in which **both** sides satisfy every AD's literal text yet the composed system misbehaves, (c) the AD tightening that closes the hole. Tier = how likely two real, independent dev agents actually diverge this way.

---

## CRITICAL

### C1 — The session-response → `mount()` plumbing is unpinned, and the repo already documents three different mount shapes

**Units:** MOODLE (plugin + `POST /api/v1/playback-sessions`) × PLAYER.
**Shared contract:** how `resume {open_attempt, position, attempts_used}`, `feature_flags`, `tier_hints`, and locale travel from the server-side session response (delivered to the plugin's PHP) into the running Player.

**Construction.** The evidence is already divergent in the companions:
- ADR-006: `EdonPlayer.mount(element, {scriptUrl, token, flags, locale})`
- ADR-014: `EdonPlayer.mount(el, {source, sink, narration, registry-extensions?, …})` — "the Moodle embed passes nothing special"
- integrations/mod-edonlesson §2.3: `EdonPlayer.mount(el, {scriptUrl, token, …})`

The MOODLE dev builds the three-line embed per ADR-006/§2.3 and passes only `{scriptUrl, token}` — fully compliant (ADR-014 told them to pass nothing special). The PLAYER dev, reading ADR-010 ("resume state … restored by the playback session — `resume` block in the session response"), expects `opts.resume` — the only documented carrier of `open_attempt`. Both compliant; composed result: resume state and the open-attempt id never reach the Player. Every reload restarts at Block 1; the ResultsSink has no attempt id to submit against (does it mint one? call an undocumented endpoint?); AD-15's "reload re-attaches and never consumes" is structurally unimplementable. The inverse build (plugin templates `resume` into the page; Player instead fetches it itself via the token — ADR-009 scopes the playback token to "resume state", implying an endpoint no document defines) fails the same way with the arrow reversed. `feature_flags`/`tier_hints`/locale have the identical unpinned path.

**Close with:** new AD (**Playback bootstrap contract**): the Player, given only `{scriptUrl, token, locale}`, fetches a single `GET /api/v1/playback/bootstrap` (token-authed) returning the pinned script URL, `resume` (exact field list + types), `feature_flags`, `tier_hints`, and `attempt` identifiers; the session response to the plugin is for the plugin's own display only and MUST NOT be re-serialized into the page. Fix ADR-006/ADR-014/§2.3 to one canonical mount signature. Pin `resume.position` semantics (block **id**, not index) in the same AD.

### C2 — Block Regeneration vs autosave: nobody owns the `revision` bump or the Block-id minting rule

**Units:** PIPELINE (Block Regeneration job) × AUTHORING (autosave block-patch + Review Workspace).
**Shared contract:** the mutable Draft — `revision` optimistic concurrency (AD-5) and Block identity across regeneration (AD-17 "replaces it atomically").

**Construction A (regen bumps revision — compliant per AD-5/AD-7).** Teacher's SPA holds revision 41, triggers Regenerate Block 3 (async job), keeps editing Block 5. Job completes server-side → revision 42. The next autosave sends `If-Match: 41` → 409. AD-5 pins only the transport ("mismatch = 409, never silent overwrite") — 409 *recovery* is unpinned. A reasonable AUTHORING agent implements "conflict → reload server copy, discard local" → every regeneration eats the Teacher's in-flight edits. Both units letter-perfect.

**Construction B (regen bypasses revision — also defensible: AD-5's revision is "for optimistic concurrency", i.e. user edits; the job is atomic on its own).** Autosave at `If-Match: 41` now succeeds against a Draft whose Block 3 silently changed; the SPA's stale local Block 3 later flows back in a patch and silently reverts the regeneration — "never silent overwrite" violated in effect while every request honored If-Match.

**Construction C (id minting).** Conventions say "Entity ids UUIDv7". PIPELINE mints a fresh UUIDv7 for the replacement Block (it is a new generated artifact — compliant). AUTHORING keys autosave patches, citation display, and pending-edit buffers on the old block id → 404s/dangling refs. Or PIPELINE preserves ids while the check harness / citation projection assumed regen ⇒ new id. Nothing pins it.

**Close with:** tighten AD-5 + AD-17: (1) Block ids are **stable slot ids minted once at the plan stage**; Regeneration preserves the Block id; publish preserves Draft Block ids into the version. (2) Regeneration **participates in the revision sequence** — the job's replace is a normal core-use-case write that bumps `revision`, and the job-complete SSE/notification carries `{block_id, new_revision}` so the SPA rebases without a 409. (3) Define 409 recovery normatively: refetch, per-block three-way rebase, surface true conflicts per-block — never wholesale discard, never blind replay.

### C3 — Completion denominator: "all renderable Blocks viewed" — renderable *according to whom?*

**Units:** PLAYER (BlockRegistry, FR-2 unknown-block omission) × MOODLE (platform API computing completion, ADR-010).
**Shared contract:** which Blocks count toward completion.

**Construction.** AD-2 minor bump ships a new optional Block type; per AD-2/AD-10 an older deployed Player build omits it from sequence and counts — compliant, mandated. ADR-010: completion fires when "all renderable Blocks are viewed … unknown types excluded per FR-2" — but the *platform* knows the type (it generated it), so a compliant server-side implementation excludes nothing. The Student views every Block their Player shows; the Player's own count completes; the server waits forever for a view mark on the omitted Block → completion never fires, no outbox row, Moodle activity completion permanently stuck, and nobody errors. Both units satisfied their texts exactly. This ignites at the *first* schema minor bump after launch — a certainty, since AD-2 exists precisely to allow them.

**Close with:** tighten AD-15: the completion denominator is the **player-declared rendered set** — at bootstrap the Player posts (via ResultsSink) the ordered list of Block ids its registry will render for this attempt; server-side completion = all declared Blocks viewed + all declared Quiz Blocks submitted. Blocks the player omits are recorded (`blocks_omitted` on the attempt) for telemetry. Forbid any server-side inference of renderability.

---

## HIGH

### H1 — `attempts_used` truth: per-Lesson counts vs per-activity limits

**Units:** MOODLE (activity settings, `attempt_limit` per session; outbox keyed by `activity_ref`) × PLAYER (retake gating from `resume.attempts_used`); the platform attempt store sits between them.
**Construction.** AD-15's letter: "attempt counts are per-Lesson." §2.1/OQ-13 encourage the same Lesson in multiple activities/courses (College-library parity). Activity A (limit 3) and Activity B (limit 1) both point at Lesson L. Student spends 2 attempts in A; opens B → platform compliantly reports `attempts_used: 2` ≥ B's limit 1 → blocked in an activity they never attempted. Worse: the completion/grade outbox rows carry the `activity_ref` of the attempt's session, so Activity B can never receive completion at all. Every unit obeys its text.
**Close with:** tighten AD-15: attempts, limits, and completion are scoped to `(lesson_id, activity_ref)`; "per-Lesson" survives only inside one activity context; cross-activity aggregation (if ever wanted) is an explicit reporting concern. Mirror the rule into integrations §2.3/§2.4.

### H2 — `job_progress` → Authoring SSE: state enum, `block_ref` semantics, replay, termination — none pinned; stage names are hot config

**Units:** PIPELINE (writes `(job_id, block_ref, stage, state, at)` rows) × AUTHORING (SSE consumer, per-Block assembly showpiece).
**Construction.** PIPELINE emits `state` from its internal enum (`pending|running|repaired|done|failed`); AUTHORING renders `queued|generating|complete`. `block_ref` at plan time predates Block existence — index? brief slug? Block id? Each agent picks differently. SSE framing (raw row vs envelope), replay-on-connect vs live-tail-only (connect after stage 2 → card shows Blocks 1–2 pending forever), and the terminal "job finished" signal are all unpinned — and AD-17 makes **stage names config-hot**, while the showpiece card must map stage → copy: one compliant `pipeline.yaml` edit silently degrades the flagship UX to the A-8 coarse floor permanently. Every behavior above is inside the letter of AD-17/ADR-005.
**Close with:** new AD (**Progress-stream contract**): pin the `job_progress` row enum, `block_ref` = plan-minted stable Block id (see C2), SSE envelope (`event:` names, JSON shape, snapshot-then-tail semantics, terminal `job_completed|job_failed` event), and a `display_key` per stage resolved through the AD-20 language catalog so stage renames are config on *both* sides.

### H3 — Publish racing autosave/regeneration: publish carries no revision

**Units:** AUTHORING (publish action + core/lessons transaction) × PIPELINE (regen job landing mid-publish).
**Construction.** AD-5 pins `If-Match` for Draft mutations only; publish mutates `published_versions`, so a compliant publish endpoint takes no revision. Pre-publish Simulation checks run headless Chromium for seconds — they cannot literally sit inside the DB transaction, so a compliant build is: read Draft → run checks → transaction(revalidate → freeze → insert). Between check-run and transaction, an autosave or a regen job commits — the inserted version contains content the Teacher never previewed, and (worse) a Simulation bundle the checks never executed: the A-35 [HARD] gate voided while every step matched AD-5's sequence.
**Close with:** tighten AD-5: publish requires `If-Match: revision`; the version-insert transaction asserts `drafts.revision == checked_revision`, else 409 (`draft_changed_since_review`) and the checks re-run. State explicitly that pre-publish checks execute against a revision-pinned snapshot.

### H4 — Quiz resubmission semantics: client localStorage outbox vs server resume state, and "which score wins" is undefined

**Units:** PLAYER (localStorage outbox + sendBeacon, PlatformResultsSink) × MOODLE (platform playback API, idempotent on `(attempt, block, uuid)`).
**Construction.** Submit for Block 5 → ack lost → uuid-X parked in the client outbox. Reload: server resume compliantly reports Block 5 unanswered (it never landed) → Player compliantly re-enables the quiz → student answers again, uuid-Y acks, feedback shown. Outbox flush then delivers uuid-X: a *different* uuid, so the idempotency rule accepts it as a second scored submission. Nothing pins one-submission-per-block, nor first/last/max-wins within an attempt — a last-write build scores the stale uuid-X over the answer the student saw feedback for; outbox grade rows disagree with the on-screen result. Every unit obeyed AD-15's letter.
**Close with:** tighten AD-15: exactly one scored submission per `(attempt_id, block_id)` — first durable ack wins; later submissions with a new uuid return `409 already_submitted` carrying the recorded result; the client outbox must reconcile against `resume`'s per-block submitted state before enabling re-answer, and `resume` must therefore include per-block submission state (feeds C1's bootstrap contract).

### H5 — Relaunch localStorage edit-replay silently clobbers a concurrent editor while honoring If-Match on every request

**Units:** GOVOPS (identity epic owns ADR-009's relaunch + "localStorage preservation of unacknowledged edits, restored after relaunch") × AUTHORING (Draft revision discipline).
**Construction.** Teacher's 8 h session dies mid-edit; unacked edits cached locally against revision 41. Overnight, the tenant_admin (ADR-009 grants edit rights over any tenant lesson) advances the Draft to revision 55. Morning relaunch lands the Teacher on the same Draft; a compliant restore flow refetches (rev 55) then replays the cached edits as block patches with `If-Match: 55` — every request individually honors AD-5, and the admin's overlapping work is silently overwritten by night-old text. "Never silent overwrite" holds at the transport and fails in effect.
**Close with:** tighten AD-5 (or fold into C2's concurrency law): locally preserved edits carry their **base revision**; if server revision ≠ base on restore, edits are staged as per-block proposals with a visible keep-mine/keep-server resolution — auto-replay is forbidden. Add the two-editor case to the mandatory test floor.

### H6 — Simulation param declaration and check-harness conventions: `params` means three different things

**Units:** PIPELINE (freecode generation prompts + template library authoring) × PLAYER (host side of protocol v1) — with the ADR-007 check harness as the third reader.
**Construction.** AD-12 pins message *names* only. Compliant PIPELINE emits `params` as a value map `{"gravity": 9.8}`; the compliant check harness needs declared-param *descriptors* to assert "every declared param maps to a native form control … asserted by DOM inspection" — it invents a convention (`data-edon-param="name"`, or descriptor array `[{id, label, min, max}]`) that the generation prompts and template authors were never told about → 100% keyboard-operability check failure → publish permanently blocked; alternatively `host:set-param {name, value}` vs `{params: {…}}` batch, and whether the sim must echo `sim:state` after set-param (check 4's pass criterion), each fork independently. All parties inside AD-12's letter.
**Close with:** tighten AD-12: the /schema protocol document must pin (1) the param **descriptor** shape in the Block payload (`[{id, label, type, min, max, step, default}]`), (2) `host:set-param {id, value}` single-param form, (3) the mandatory `sim:state` echo (`{params: {id: value…}}`) as the check-4 pass criterion, (4) the DOM marker (`data-edon-param`) that check 3 asserts — and state that generation prompts and template guidelines are *derived from* this document.

### H7 — `action_type` enforcement vs the identity-free adapter request: the reserve point can't know what it's metering

**Units:** GOVOPS (governance in the adapter call path, policies per `action_type`) × PIPELINE/DIAGRAM (callers).
**Construction.** AD-3/ADR-011 pin the adapter request to `(workload, messages, params, accounting_ref)` — no `action_type` field, and `accounting_ref` resolves "only inside the telemetry writer", i.e. *after* the call. AD-8 pins enforcement "in the adapter call path: reserve before the call" — but `block_regeneration` and `lesson_generation` are distinct `action_type`s sharing the same `workload`s. A compliant GOVOPS build reserves per `workload` (all it can see) → block-regen quotas silently un-enforceable; a compliant PIPELINE build assumes the adapter handles it and calls no reserve API of its own. Neither is wrong by any AD's text; the composed system has a governed-vocabulary quota that no code can apply.
**Close with:** tighten AD-3 + AD-8 jointly: the adapter request carries a mandatory **`governance_ref`** = `(action_type, accounting_ref)` — still identity-free, satisfying ADR-011 — and reservation keys on `action_type` from it; the telemetry writer alone resolves `accounting_ref` to tenant/pseudonym, unchanged.

### H8 — Who implements the OQ-9 intake pause? Three epics can each compliantly assume another does

**Units:** GOVOPS (policy engine + adapter hook) × PIPELINE (generation intake endpoint) × AUTHORING (bootstrap banner).
**Construction.** AD-8: enforcement lives "in the adapter call path" *and* "generation intake pauses with explicit notice" — two enforcement points, no named owner for the second. GOVOPS compliantly builds reserve/settle in the adapter only ("no ungoverned way to spend" — satisfied). PIPELINE compliantly enqueues any request, expecting a `budget_paused` rejection that never comes. Result: jobs enqueue, start, and die at the first LLM call's failed reserve — surfacing as `generation_failed` ("try again") instead of the OQ-9 pause banner; the Authoring bootstrap "banner state" (ADR-013) has no defined field to read. Also unpinned: a job already queued when the budget exhausts — reject at fetch, or fail at first reserve, and with which Teacher-facing reason code.
**Close with:** tighten AD-8: name the **two mandatory enforcement points** — (1) pre-enqueue governance check inside the generation-intake use-case (returns `budget_paused|quota_exhausted|rate_limited` machine codes), (2) adapter-path reserve as backstop; pin the Authoring bootstrap response field (`governance_state`) the banner reads; pin the already-queued-job rule (fail fast at fetch with `budget_paused`, no repair retry, no spend).

---

## MEDIUM

### M1 — Heavy-asset transfer size: the Player must know bytes *before* fetching, and no one owns putting them there
**Units:** SCHEMA/PIPELINE × PLAYER. AD-11's tap-to-load labels and the Constrained ceiling (glTF > 2.5 MB ⇒ poster-only) require the size pre-download. The frozen `manifest.json` has sizes but the Player receives the *script*; a compliant SCHEMA omits a `transferSize` field (AD-11 never asks for one), a compliant PLAYER then either always-loads (ceiling unenforceable) or issues HEAD requests the X-Accel-Redirect authz path was never designed for. **Close with:** AD-2/AD-11 addendum — asset references in the script carry `transferSize` (bytes), populated at assemble/freeze; the Player's ceiling and labels read only that field.

### M2 — Citation object optionality: a strict schema + the WI-RAG-1 fallback = 100% job failure
**Units:** SCHEMA × PIPELINE. ADR-004's projection lists `locator`; a compliant SCHEMA agent makes `locator` required. edon-rag §5 (WI-RAG-1) says locators may be absent and pipeline "stores whatever metadata exists" — compliant PIPELINE omits the field → no Draft ever validates against the deployed corpus, and the recorded-fixture CI (fixtures having locators) never catches it before staging. **Close with:** AD-2 addendum — pin the citation object's required set to the guaranteed fields only (`sourceChunkId`, `documentTitle`, `excerpt`); `locator`, `documentId`, `tags` optional; the fixture corpus MUST include a no-locator citation fixture.

### M3 — Flag-off Simulation: delivery-time stripping vs Player poster fallback
**Units:** MOODLE-API/GOVOPS × PLAYER. AD-18: flags "evaluated at playback bootstrap" — a compliant server build implements that as filtering Simulation Blocks out of the delivered script; the compliant Player expects the Block present to render Poster fallback (A-14). Stripping shifts "Block n of N", resume positions, and the completion denominator between sessions of one pinned attempt. **Close with:** AD-18 addendum — flags never alter delivered script content; the bootstrap response carries the flag map (C1) and the Player degrades presentation. Server-side stripping is forbidden.

### M4 — `budgets.json` has consumers in three languages and no schema, units, or single readable location
**Units:** PLAYER (JS CI) × PIPELINE (py validators) × GOVOPS (ingest CLI, sim-check budget). The source tree pins it under `backend/src/edon/config/` — which player CI can't naturally read, so a compliant PLAYER agent scaffolds its own copy → drift; key naming and units (kB vs bytes vs MB; is AD-12's 1.5 MB sim budget inside or hardcoded?) fork per agent. **Close with:** AD-11 addendum — move `budgets.json` to repo root (or `/schema`), publish its own JSON Schema in `/schema`, all values in **bytes**, enumerate its four consumers, and include AD-12's simulation budgets in it (AD-18 already demands they be config).

### M5 — Teacher-role playback sessions write real grades
**Units:** MOODLE × PLAYER. §2.3 accepts `lms_user_role`; teachers routinely open activities. A compliant platform mints a normal session; the compliant Player always mounts `PlatformResultsSink` (the no-op sink is preview-only, ADR-014) → teacher attempts, outbox grade rows, and a plugin gradebook write for a non-student. **Close with:** AD-15 addendum — non-student playback sessions are marked `observer: true` in bootstrap; the Player mounts the no-op sink for them; the platform refuses attempt creation and outbox rows for observer sessions.

### M6 — Diagram review queue: row content and the invalidation key are undefined across the seam
**Units:** DIAGRAM × AUTHORING. AD-21 pins semantics ("Mark invalid" clears row + deletes cache entry) but not the interface: a compliant DIAGRAM stores normalised text + cache key; the compliant AUTHORING card wants the raw request text, the SVG, reporter note, and duplicate-report count, and calls invalidation by `diagram_id` while the cache is keyed by normalised text. **Close with:** AD-21 addendum — pin the review-queue row (`diagram_id`, raw + normalised text, svg asset ref, report count, latest note, requested_at) and make `diagram_id → cache_key` a stored column so invalidation is by id; both actions are core use-cases the Authoring UI calls (AD-7).

### M7 — The diagram cache key as a storage path segment
**Units:** DIAGRAM × GOVOPS (storage law). ADR-012 pins `…/diagram-cache/{key}.svg`; the AD-17 normaliser preserves `/`, `.`, and arbitrary Unicode — a compliant DIAGRAM agent using normalised text as `{key}` produces invalid or path-escaping keys (`../`) that the tenant-prefix helper does not defend against (it prepends; it doesn't sanitise). **Close with:** AD-17/AD-9 addendum — the *cache key* is `sha256(normalised_text)` hex; normalised text is stored data, never a path segment; the StorageDriver rejects keys outside `[a-z0-9/_\-.]` with no `..` segments.

---

## LOW

### L1 — Who renders limit copy: platform-interpolated strings vs client-side language-key resolution
**Units:** GOVOPS × AUTHORING/PLAYER. The conventions row says user-facing copy is "resolved from language keys client-side — raw errors never rendered"; AD-20/AD-21/integration docs have the platform return fully interpolated humane strings. Compliant builds pick opposite sides per surface → banners showing machine codes, or double-templated text. **Close with:** AD-20 addendum — chat/diagram API returns rendered `message` (plugin is dumb); first-party UIs (Authoring, Player) receive `code + params` and resolve client-side; state the split explicitly.

### L2 — `curriculumRef {value, source}` vs the picker's flat `curriculum_ref`
**Units:** AUTHORING/SCHEMA × MOODLE. Script stores the object (AD-2); §2.1 returns a flat field. A compliant serializer emits the object → picker shows `[object Object]`; and whether the teacher override or pipeline value is displayed is unpinned. **Close with:** one line in integrations §2.1 — `curriculum_ref` is the string `value` (teacher override wins when `source: "teacher"`).

### L3 — Two "one" normalisers and the meaning of "strip trailing punctuation"
**Units:** PIPELINE × DIAGRAM. AD-17 pins the step list but not the module: each epic compliantly implements "the AD-17 normaliser" locally, and "trailing punctuation" (Unicode `P*` vs ASCII set; strip-once vs iterate) forks silently → cache/fingerprint misses only (soft, invisible). **Close with:** AD-17 addendum — the normaliser is one named function in `core/text.py` (`normalise_key`), Unicode-category `P*`, applied iteratively, with a shared fixture vector in `/schema` fixtures; both consumers import it, CI asserts no second implementation.

---

## Roll-up of required spine changes

| Action | Covers |
| --- | --- |
| **New AD — Playback bootstrap contract** (single token-authed bootstrap endpoint; pinned `resume` shape incl. per-block submission state; canonical mount signature; observer sessions) | C1, H4, M3, M5 |
| **New AD — Draft concurrency law** (plan-stage stable Block ids; regen in the revision sequence; 409 recovery + restore/rebase rules; publish `If-Match`) | C2, H3, H5 |
| **Tighten AD-15** (player-declared completion denominator; `(lesson, activity_ref)` attempt scope; one scored submission per block) | C3, H1, H4 |
| **New AD — Progress-stream contract** (row enum, block_ref = Block id, SSE envelope, snapshot+tail, terminal events, stage `display_key`) | H2 |
| **Tighten AD-12** (param descriptors, set-param form, sim:state echo, `data-edon-param` marker) | H6 |
| **Tighten AD-3/AD-8** (`governance_ref` on adapter requests; two named enforcement points; bootstrap `governance_state`; queued-job-on-pause rule) | H7, H8 |
| **Minor addenda** to AD-2 (citation optionality, `transferSize`), AD-11 (budgets.json schema/location/bytes), AD-17/AD-9 (hashed cache key, normaliser module), AD-18 (no content stripping), AD-20 (rendering split), AD-21 (review-row shape), integrations §2.1 | M1, M2, M4, M6, M7, L1, L2, L3 |

*Reviewer: adversarial lens, architecture run 2026-07-17.*
