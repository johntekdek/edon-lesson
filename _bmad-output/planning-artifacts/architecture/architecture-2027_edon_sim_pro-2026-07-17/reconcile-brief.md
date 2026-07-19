# Reconciliation Review — Architecture vs Product Brief

**Reviewed:** ARCHITECTURE-SPINE.md, ADR-001..ADR-013, docs/integrations/ (3 contracts), project-context.md (for §12.3 compliance)
**Source of truth:** `_bmad-output/planning-artifacts/edon-lesson-studio-product-brief.md`
**Date:** 2026-07-17

## Verdict summary

The architecture is a strong match to the brief. The two load-bearing invariants (generate-once, review gate) are realized as *structural* system properties, not conventions: the playback path contains zero governed LLM calls (ADR-013 "structural SM-4 claim"), Published Versions are self-contained and DB-immutable (AD-5: no UPDATE/DELETE grant), and the sanitisation gate is the only path into storage for LLM SVG (AD-13). The external-systems boundary (§8) is exemplary — the edon-rag contract flags every gap as a WI-RAG work item, never an edit. Five of the six required ADR topics are cleanly present; the §10 extension-points topic is the one packaging gap. Of the six V3 seams, (a)(c)(d)(f) are genuinely convincing, (b) is convincing player-side, and (e) is convincing for assets but hand-wavy on the Player's runtime results path.

**Counts: 0 Critical / 1 High / 3 Medium / 5 Low**

---

## Critical

None.

## High

### H-1. §12.3 requires ADRs for "the §10 extension points" — seams (b), (c) and the player-composition decision have no ADR rationale record
- **Brief anchor:** §12.3 ("ADRs for, at minimum: … and the §10 extension points")
- **Architecture location:** Seams live only in ARCHITECTURE-SPINE.md AD-10 + the "V3 seams" table; ADR-005/006/010/012/013 cover seams (a)(e)(f)(d) piecemeal, but `BlockRegistry`/`LessonDeliverySource`/`NarrationProvider` (seams a/b/c as decisions) have no ADR home — ADR-006 is bundling/embedding only.
- **Fix:** Add ADR-014 "Player composition and V3 extension interfaces" (registry + delivery source + narration provider, alternatives considered), or extend ADR-006 and add an explicit §10-seam → ADR/AD cross-reference table.

## Medium

### M-1. Seam (e) demonstration covers assets but not the Player's runtime platform calls — SCORM export needs a results path
- **Brief anchor:** §10(e), §7 (offline/SCORM "cheap to add as a fast-follow")
- **Architecture location:** AD-9/ADR-012 (publish freeze, manifest, `v{n}/` = the package), ADR-006 ("`file://`-safe CompleteScriptSource") demonstrate static self-containment convincingly. But view marks, quiz submission, and resume state are hardwired to platform endpoints (AD-15, ADR-010) with no sink abstraction — a real SCORM package must report scores via the SCORM RTE API, and offline must degrade these calls. The seam table's "a packager that zips…" is silent on this.
- **Fix:** Name a Player-side results/telemetry sink interface (or an explicit offline degrade rule for view/submit/resume) in AD-10 or the new ADR-014, so seam (e) is extension-complete beyond assets.

### M-2. AD-2 "major = breaking (defined cannot-play state)" is in tension with brief §6 "published lessons must remain playable forever"
- **Brief anchor:** §6 (forward-compatible by construction; playable forever)
- **Architecture location:** ARCHITECTURE-SPINE.md AD-2. Published Versions are immutable (AD-5), so they can never be migrated in place; if a future major bump ever retired old-major renderers, existing published lessons would break — violating the brief's invariant.
- **Fix:** Add one sentence to AD-2: the Player retains renderers for every shipped major version forever; "cannot-play" applies only to scripts *newer* than the deployed Player.

### M-3. §12.5 sequencing: every pre-Moodle epic needs an auth path, but the only documented Launch Token minter is the (late-epic) Moodle plugin
- **Brief anchor:** §12.5 (schema → pipeline → player → review/publish → block types → *then* Moodle module)
- **Architecture location:** ADR-009 ("no standalone login exists"), docs/integrations/mod-edonlesson-platform-api.md §2.2 (plugin-minted HS256 JWT). Authoring sessions — and via preview, the entire walking-skeleton/player/review phases — bootstrap only through a token the plugin mints. No code forward-dependency exists (any HS256 signer with the tenant secret can mint one), but the architecture never says so, so early-epic DoD/end-to-end verification has no sanctioned entry path.
- **Fix:** Add one line to ADR-009 (or the deferred table): a dev/staging token-minting CLI (same claims, same secret) is the sanctioned pre-plugin launch path.

## Low

### L-1. Seam (b) is demonstrated player-side only; the platform's incremental-delivery surface is unaddressed
- **Brief anchor:** §10(b)
- **Architecture location:** AD-10(b) async block-iterator signature is the right load-bearing detail; the seam table's "new source (SSE/WebSocket) registered at mount" implies a future platform streaming endpoint that no AD/ADR sketches.
- **Fix:** One sentence noting the backend counterpart is a new additive endpoint on the existing API version (no change to publish/storage model).

### L-2. Seam (f): LTI 1.3 AGS is push-based and needs a fifth credential kind, versus "pull + ack" and AD-14's "exactly four credential kinds, no others"
- **Brief anchor:** §10(f), §7 (LTI out of scope)
- **Architecture location:** AD-14, AD-16, ADR-010 ("LTI 1.3 later consumes the same outbox") — sound, since a platform-side LTI connector can drain the outbox and push via AGS, but the "exactly four … no others" phrasing reads as a closed invariant the LTI extension would have to break.
- **Fix:** Reword AD-14 to "four credential kinds at MVP; new LMS connectors add kinds inside the identity module" and note the LTI connector as an outbox *consumer* in AD-16.

### L-3. block_edon_ai enhancement adds a third-repo work stream beyond the brief's §12.4 two-repo plan
- **Brief anchor:** §12.4 (repos: `edon-lesson` + `mod_edonlesson`); §5 FR-D.16 ("within the existing AI chat") makes some chat-side change unavoidable
- **Architecture location:** Spine scope line + docs/integrations/block-edon-ai-diagram-api.md (records it as stakeholder decision OQ-12, minimal surface WI-CHAT-1..3)
- **Fix:** Carry the OQ-12 repo-plan extension into the sign-off batch as an explicit stakeholder confirmation item.

### L-4. Brief §6 "do not preclude" list: adaptive branching metadata is never explicitly shown as non-precluded
- **Brief anchor:** §6 (reserved for V3: dialogue turns, adaptive branching metadata, streaming)
- **Architecture location:** AD-2 additive-minor rule + AD-10 `LessonDeliverySource` (a branching-aware source could sequence blocks) cover it in substance, but only dialogue turns and streaming are called out.
- **Fix:** Add "adaptive branching metadata = optional additive fields + a sequencing-aware delivery source" to the V3 seam table or AD-2.

### L-5. §9 "object storage" lands as a VPS filesystem driver at launch
- **Brief anchor:** §9 (Data: object storage for lesson assets with tenant-scoped paths)
- **Architecture location:** ADR-012 — `StorageDriver` port, tenant-prefixed keys, documented S3-compatible swap, MinIO/AGPL exclusion. Functionally compliant and well-reasoned; listed only so the launch-driver reading of "object storage" is confirmed at sign-off.
- **Fix:** Include ADR-012's filesystem-at-launch posture in the stakeholder sign-off batch.

---

## Section-by-section confirmation (checked, no findings)

- **§10 seam judgments:** (a) **Convincing** — registry entry + schema minor bump + type-agnostic pipeline stage, with CI unknown-block/future-version fixtures making forward-compat continuously proven. (b) **Convincing player-side** (see L-1). (c) **Convincing** — named `NarrationProvider` interface with method set; pre-gen TTS = new provider + audio-ref minor bump, with AD-9 freeze covering audio assets. (d) **Strongest seam** — governance is generic by construction (`action_type` rows), enforced in the one adapter call path ("no ungoverned way to spend"); ADR-013 states the V3 change is literally policy rows. (e) See M-1. (f) **Convincing** (see L-2) — LMS-agnostic nouns, opaque `lms_user_id`, Moodle knowledge confined to plugin, pull+ack outbox.
- **§12.3 ADR checklist:** backend framework (ADR-001 ✓, decides FastAPI vs Flask with recorded divergence rationale — §9's "silence is not acceptable" met); lesson storage/versioning (ADR-004 ✓); generation pipeline incl. queueing/caching/cost telemetry (ADR-005 + ADR-003 ✓ — idempotency fingerprint, prefix caching, per-lesson cost aggregation); player embedding for Moodle (ADR-006 ✓); simulation sandboxing (ADR-007 ✓); extension points (H-1). `project-context.md` generated/extended with clean-room constraint and team standards verbatim ✓.
- **§8 boundary:** never assumes source access or edits — edon-rag gaps are WI-RAG-1..4 work items with MVP fallbacks; Moodle reached only via `mod_edonlesson` + Moodle APIs (outbound-only from Moodle); LLM access solely via the workload-keyed adapter, no hardcoded model strings (AD-3, ADR-002 config-only switch proven by the benchmark harness itself); 3D licence metadata mandatory at ingest and frozen into the manifest ✓.
- **§9 constraints:** Python 3.12 ✓; JS/JSX no-TS ([HARD] in project-context §2) ✓; self-contained IIFE, no Next.js host ✓; Three.js ✓; PostgreSQL ✓; VPS/nginx/systemd/certbot ✓; horizontal worker scaling path ✓; SVG allowlist sanitiser ✓; iframe sandbox `allow-scripts` + `default-src 'none'` CSP, no network ✓; tenant isolation with RLS defense-in-depth ✓; per-tenant CORS, no wildcard ✓; `.env.example` discipline ✓; dual-valid keys = day-one rotation ✓; clean-room constraint verbatim in project-context §5, no OpenMAIC references anywhere in the deliverable ✓.
- **§11 risks with architecture ownership:** simulation dual-mode coexistence — `mode: template|freecode` in the schema, identical sandbox + protocol, ship choice is config, ADR-002 benchmark decides the default (genuinely coexistent, not a fork) ✓; poster fallback per block — ingest-time poster render, watchdog → poster, flag-off → poster, tap-to-load tiers ✓; cost creep — reserve→settle budgets, per-call telemetry, $2 `cost_alert`, cache-hits-charge-nothing, OQ-9 exhaustion semantics with replay never blocked ✓; generation quality — pipeline-as-config (AD-17), tuning is a config release ✓.
- **Invariants as system properties:** generate-once — published replay path structurally contains no LLM/edon-rag calls (embedded citations/excerpts, frozen assets, NFR-4); regeneration explicit; idempotency fingerprint. Review gate — students reach only Published Versions via playback sessions; publish is one transaction with revalidation + checks + freeze; DB-enforced immutability; sole exception is the sanitised diagram path, itself gated by the single-server-side sanitiser ✓.
- **§12.5 sequencing:** schema package is standalone and consumed by both sides (first ✓); pipeline skeleton needs only adapter+rag client+drafts (governance-in-path *forces* the brief's "hardening threaded throughout" ✓); player renders drafts via preview-parity mode before publish exists ✓ (subject to M-3 auth bootstrap); block types are incremental registry/stage/config additions in diagram → model3d → simulation order ✓; outbox rows accumulate harmlessly before the plugin epic drains them ✓; student diagrams reuse core/diagrams + sanitiser + governance already built ✓. No code-level forward dependencies found.
