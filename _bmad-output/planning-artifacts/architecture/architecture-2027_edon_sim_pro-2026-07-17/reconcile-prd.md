# Reconciliation Review — Architecture vs PRD/Addendum

**Deliverable:** `ARCHITECTURE-SPINE.md` + ADR-001..013 + docs/integrations/* (run 2026-07-17)
**Source of truth:** `prd.md` + `addendum.md` (prd-2027_edon_sim_pro-2026-07-07, final)
**Reviewer sweep:** FR-1..FR-29 consequences · NFR-1..NFR-9 · SM-1..SM-5 + SM-C1..C3 measurability · addendum §1 ADR agenda · OQ-1..OQ-17 decided forms · A-1..A-35 architecture ownership · scope fence · Glossary vocabulary.

**Verdict: no invariant (I-1..I-4) or [HARD] rule is contradicted; no FR is dropped; every addendum §1 agenda item has an ADR/AD home (including the project-context.md §9 extension, verified appended, additive).** The findings below are where PRD requirements landed distorted, half-landed, or were quietly extended.

**Counts: Critical 0 · High 2 · Medium 8 · Low 8**

---

## Critical

None.

---

## High

### H-1 — Generation idempotency index conflicts with creator-owned Draft privacy
- **PRD anchor:** FR-7 + A-7 (idempotency keyed on Tenant/course/topic/guidance) × OQ-13 / FR-10 / §4.3 ("Drafts are private to their creator")
- **Architecture:** ADR-004 Consequences — "Idempotency cache for generation (A-7) is a unique index on `drafts.request_fingerprint` **per tenant**"
- **Issue:** Two Teachers in one Tenant submitting the same normalised request (same course, popular topic — a mainline case) either collide on the unique index (Teacher B's generation blocked with no PRD-sanctioned behavior) or Teacher B is served Teacher A's *private* Draft — quietly contradicting the OQ-13 creator-owns decision. FR-7's idempotency guards *accidental resubmission*, which is per-author by nature.
- **Fix:** Scope the fingerprint per owner — unique on `(tenant_id, owner_user_id, request_fingerprint)` — and state that idempotent return only matches the requesting Teacher's own Draft.

### H-2 — "Writeback failures are logged as Structured Events" cannot be emitted under the pull+ack outbox
- **PRD anchor:** FR-23 consequence ("Writeback failures are logged as Structured Events and are retriable…") + FR-27 canonical taxonomy ("writeback failure and retry") + SM-3
- **Architecture:** ADR-010 ("undelivered rows simply survive to the next run — that is the whole retry mechanism"); AD-7 substitutes `writeback_overdue`; mod-edonlesson doc §2.4 (plugin writes to gradebook, then acks)
- **Issue:** Plugin-side gradebook/completion write failures are invisible to the platform (no ack ⇒ silent redelivery); the taxonomy's `writeback failure`/`retry` events are never produced, and SM-3's 100%-within-24h evidence degrades to a negative-only signal (`writeback_overdue` after ageing). Retriability lands; the event consequence does not.
- **Fix:** Extend the ack contract to ack-with-status (or add `POST /api/v1/outbox/nack {delivery_id, reason}`) so the platform emits `writeback_failed`/redelivery events per FR-27 — or batch an explicit PRD taxonomy amendment for sign-off.

---

## Medium

### M-1 — NFR-3 "secrets via environment configuration only" quietly widened to DB-stored secrets
- **PRD anchor:** NFR-3
- **Architecture:** Spine Consistency Conventions ("secrets only via env **or encrypted tenant-config columns**"); ADR-009 (per-tenant signing secrets, edon-rag keys in tenant config, encrypted with a platform KEK); ADR-011 (per-tenant salts)
- **Issue:** Per-tenant secrets at rest in PostgreSQL is a defensible design (~60 tenants can't live in env) but it contradicts NFR-3's letter and is nowhere flagged as a deviation.
- **Fix:** Record the deviation explicitly (env holds the KEK; per-tenant secrets are envelope-encrypted under it) in ADR-009/spine and add it to the sign-off batch.

### M-2 — SM-1 not computable from the events+telemetry substrate: no clock-start event
- **PRD anchor:** SM-1 ("clock starts at request submission, queue time included") + FR-27 taxonomy (has `lesson generated`/`generation failed` but no request/queued event) + AD-19's own claim ("SM-1..SM-5 … computable from them alone")
- **Architecture:** AD-7 closed taxonomy; ADR-003/005 (`job_progress` rows, but ADR-011 retains them only 30 days)
- **Issue:** The initiation timestamp lives only in job tables/progress rows (30-day retention), so median/p90 initiation→ready is not computable from events + Cost Telemetry alone beyond that window.
- **Fix:** Specify that `lesson_generated`/`generation_failed` events carry `requested_at` (or add a `generation_requested` event to the taxonomy via the sign-off batch).

### M-3 — SM-C2 (Block-type richness) not computable from the declared analytics substrate
- **PRD anchor:** SM-C2 (share of Published Versions containing interactive Blocks) + FR-27 ("sufficient to power a future analytics dashboard")
- **Architecture:** AD-19 (events + telemetry are "the only analytics substrate"; counter-metrics "computable from them alone") — but no event payload carries Block composition
- **Issue:** Block-type mix lives only in `published_versions.script` JSONB; the AD-19 computability claim fails for SM-C2 as specified.
- **Fix:** Specify a block-type summary (`block_types: {...}` counts) in the `lesson_published` event detail.

### M-4 — Zero-cost cache-hit telemetry has no specified emission point (adapter path is bypassed on hits)
- **PRD anchor:** FR-21 consequence ("Cache hits and misses are recorded in Cost Telemetry") + FR-27 consequence ("Diagram cache hits are additionally recorded as zero-cost telemetry events") + SM-5
- **Architecture:** AD-3 ("Cost Telemetry and governance execute in the adapter call path"); AD-8/ADR-013 (cache checked *before* any LLM call — so hits never reach the adapter)
- **Issue:** The only defined telemetry writer sits on a path cache hits never traverse; the `diagram served from cache` *event* exists, but the PRD's zero-cost *telemetry* row does not land anywhere specified.
- **Fix:** State in ADR-013 (or AD-19) that the diagram service writes a zero-cost Cost Telemetry row (no token fields, `cache_hit: true`) on every cache hit.

### M-5 — Normalisation rules assigned to architecture (A-7, FR-21) were never decided
- **PRD anchor:** A-7 ("exact normalisation is an architecture decision"), FR-7, FR-21 ("normalised request key")
- **Architecture:** ADR-004 (`request_fingerprint` — mechanism only); spine ER (`DIAGRAM_CACHE: normalised key` — name only)
- **Issue:** Neither the generation-idempotency nor the diagram-cache normalisation (case/whitespace/punctuation folding of topic, guidance, request text; inclusion of course_ref) is specified — the PRD explicitly delegated this decision to architecture and it did not land.
- **Fix:** Define both normalisation algorithms in ADR-004/ADR-013 (fields included, canonicalisation steps, hash).

### M-6 — Event taxonomy extended (5 new types) without the PRD-note/confirmation AD-7 itself requires
- **PRD anchor:** FR-27 consequence ("this FR's event list is the single canonical taxonomy") + §0 scope fence (changes need explicit stakeholder confirmation)
- **Architecture:** AD-7 ("approved extensions": `diagram_review_completed`, `diagram_invalidated`, `operator_action`, `cost_alert`, `writeback_overdue`) — labelled "approved" though the .memlog sign-off batch does not include them
- **Issue:** The extensions are all justified by architecture mechanics, but the taxonomy is a PRD-canonical contract and the additions ride on an approval that hasn't happened.
- **Fix:** Add the five event types (plus any from H-2/M-2) to the batched end-of-run confirmation list; drop the word "approved" until then.

### M-7 — Publish-time asset freeze can alter the script the Teacher previewed (FR-9/FR-11 testable consequence)
- **PRD anchor:** FR-9 consequence ("publication does not alter the script the Teacher previewed") + FR-11
- **Architecture:** AD-9 / ADR-012 ("Published Versions reference frozen paths only" — draft assets live under `…/draft/`, frozen under `…/v{n}/`); ADR-004 publish transaction
- **Issue:** If Lesson Scripts embed asset *paths*, publish rewrites the script (draft→frozen paths), violating the FR-9 consequence; if they embed stable asset *ids* resolved via `asset_manifest`, it holds — but neither is specified.
- **Fix:** Specify that scripts reference assets by stable id and the version's `asset_manifest` maps id→frozen path (script bytes unchanged by publish).

### M-8 — Budget-overrun bound widened from "at most one job" to "at most the running jobs"
- **PRD anchor:** FR-26 consequence / A-29 ("bounded overrun of **at most one job**")
- **Architecture:** ADR-013 ("bounded overrun of at most **the running jobs**, per FR-26") + ADR-003 (per-queue concurrency, shared queue across tenants)
- **Issue:** With per-tenant generation concurrency > 1 (multiple Teachers), N in-flight jobs all run to completion — a quiet loosening of the PRD's stated bound, cited as if it were FR-26.
- **Fix:** Either cap in-flight `lesson_generation` at 1 per tenant, or batch the revised bound ("at most the in-flight jobs, concurrency-capped at N") for stakeholder confirmation.

---

## Low

### L-1 — Container diagram omits the synchronous diagram LLM path
- **PRD anchor:** FR-19/FR-21 · **Architecture:** spine System containers (LLM edge from `WK` only) vs block-edon-ai doc §2.1 (synchronous, 60 s, in the API process)
- **Fix:** Add `API --> LLM` (diagram workload) to the container diagram.

### L-2 — Addendum names four per-workload keys; AD-3 defines three (`embeddings` absent)
- **PRD anchor:** addendum §1 ADR-002 item · **Architecture:** AD-3 workload list; ADR-002 ("embeddings not benchmarked — fixed inside edon-rag")
- **Fix:** One sentence in AD-3 noting `embeddings` is deliberately out of the adapter (lives in edon-rag, per ADR-002) so the divergence is visibly intentional.

### L-3 — Cost Telemetry field list ([HARD]) never enumerated in the deliverable
- **PRD anchor:** FR-27 / Glossary "Cost Telemetry" (tokens in/out, computed cost, Tenant, user, workload, cache hit/miss, latency) · **Architecture:** AD-19/ADR-005 name only accounting dimensions
- **Fix:** Enumerate the telemetry table columns (incl. cache hit/miss and latency) in AD-19 or ADR-011.

### L-4 — Glossary "version history of Drafts" vs one mutable Draft per Lesson
- **PRD anchor:** Glossary "Lesson" · **Architecture:** ADR-004 (`lesson_id` unique on `drafts`, history via `revision` int only)
- **Fix:** Note in ADR-004 that Draft history is the revision counter (no prior-draft snapshots) — a deliberate reading of the Glossary, batched for visibility.

### L-5 — Curated Model Library "curriculum-mapped" attribute has no home in the library index
- **PRD anchor:** Glossary "Curated Model Library"; FR-16 · **Architecture:** ADR-012 ingest (licence metadata, budgets, poster — no curriculum/subject mapping field), yet ADR-005 `model3d` stage selects "from the Curated Model Library index"
- **Fix:** Add curriculum/subject tags to the library index row spec (also feeds the OQ-6 seeding decision).

### L-6 — NFR-9(a) narrowed to structural identifiers; free text passes unscrubbed
- **PRD anchor:** NFR-9(a) ("no Student personal identifiers in any prompt") · **Architecture:** ADR-011 ("free-text user inputs pass through as content… no PII scrubbing in MVP")
- **Fix:** Honest and probably right — add this interpretation to the sign-off batch as an explicit NFR-9 reading, not just an ADR aside.

### L-7 — FR-3 "Backend and Player consume the same schema package" satisfied only at toolchain time
- **PRD anchor:** FR-3 consequence · **Architecture:** AD-10 ("no runtime schema validation in the Player"), schema/js ajv wrapper is CI-only
- **Fix:** Fine as designed; record that the FR-3 single-source test is asserted at build/CI (fixtures) so epics don't write a runtime-validation test the Player will fail.

### L-8 — MODEL_ASSET/SIM_TEMPLATE modelled tenant-owned vs PRD "internal" platform library
- **PRD anchor:** Glossary "Curated Model Library" (internal collection); §11 template library · **Architecture:** spine ER (`TENANT ||--o{ MODEL_ASSET`), self-flagged as "final call at schema-migration time"
- **Fix:** Already flagged in the spine — carry it into the sign-off batch so the platform-global-with-visibility-rules default is the recorded intent.

---

## Sweep coverage — verified clean (no finding)

- **FRs fully landed:** FR-1/2/3 (AD-2, A-26 ratified), FR-4/5/6/8 (AD-17, ADR-005, A-5), FR-9 preview parity (ADR-006), FR-10 incl. Draft discard + A-28 map, FR-11/12 (DB-enforced immutability; "not available" state), FR-13/14 (registry + narration provider, A-9), FR-15/OQ-4/OQ-14 (AD-15/ADR-010), FR-16 (selection-never-geometry), FR-17/A-35/A-11 (extended, not narrowed), FR-18/OQ-16 (budgets.json, no-WebGL posters, CI low-spec), FR-19/20 (AD-13, Mermaid no exemption), FR-22, FR-24, FR-25 (AD-6/ADR-008 RLS), FR-26/OQ-9 verbatim + A-3/A-14, FR-28 (label/report/spot-checks), FR-29/OQ-11 (ADR-009; no course enumeration — the picker lists lessons, not courses).
- **NFRs:** NFR-1/2/4/5/6/7 (MinIO excluded; permissive stack)/8 clean; NFR-3 clean except M-1; NFR-9 clean except L-6.
- **SMs:** SM-2, SM-4 (structural zero-LLM replay claim in ADR-013), SM-5 (events), SM-C1, SM-C3 computable; SM-1/SM-C2/SM-3 per M-2/M-3/H-2.
- **Addendum §1 agenda:** every item has an ADR/AD home; project-context.md §9 extension appended additively, [HARD] untouched; V3 seams a–f all demonstrated as extensions; cost-economics rules (config-only migration, CPU-only VPS never a generation host) present.
- **OQ decided forms:** OQ-1..4, 8..17 all traceable; OQ-5 mechanism + decision rule in ADR-002/007 (stakeholder confirmation correctly batched); OQ-6 correctly deferred to stakeholder.
- **Assumptions with architecture ownership:** A-2, A-8, A-13, A-14, A-26, A-29, A-35 all landed; A-7 per M-5.
- **Scope fence:** no PRD non-goal built (no dashboard UI, no LTI, no SCORM, no standalone login, no text-to-3D, no server TTS); additions beyond the PRD (tap-to-load, Showcase tier, relaunch-into-Draft, keyboard-operability checks, diagram alt/long-description) all trace to the UX sources named in the spine front matter.
- **Glossary vocabulary:** used verbatim throughout (Tenant/Draft/Published Version/Regeneration/Quota-vs-Rate-Limit/Budget Ceiling/Launch Token/Grounding Chunks) — exceptions only L-4/L-5.
