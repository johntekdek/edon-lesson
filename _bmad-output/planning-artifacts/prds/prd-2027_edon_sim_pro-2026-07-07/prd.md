---
title: e-DON Lesson Studio
status: final
created: 2026-07-07
updated: 2026-07-18
---

# PRD: e-DON Lesson Studio

## 0. Document Purpose

This PRD is the Phase 2 (Planning) artifact for e-DON Lesson Studio, written for the product stakeholder and the downstream BMAD workflows (UX design, architecture, epics and stories). Its feature scope derives strictly from the Product Brief's §5–§7 (`_bmad-output/planning-artifacts/edon-lesson-studio-product-brief.md`); metrics, constraints, and context draw on the brief at large. It does not restate *how* the product is built — build rules live in the authoritative `_bmad-output/project-context.md`, and technical depth that belongs downstream is preserved in this run's `addendum.md`. Vocabulary is anchored in the Glossary (§3); features are grouped with globally numbered FRs nested; inferences are tagged inline as `[ASSUMPTION]` and indexed in §13. **Scope changes in either direction against the brief require explicit stakeholder confirmation.** Stakeholder decisions dated 2026-07-07 (recorded in §12 and `.memlog.md`) resolved the open questions and authorised the scope refinements marked "stakeholder decision" throughout.

## 1. Vision

e-DON Lesson Studio turns an institution's own curriculum corpus into interactive, reviewed, gradebook-connected lessons. It is the next evolution of the deployed e-DON SIM PRO product — a Moodle-based LMS with RAG-powered AI assistance serving ~60 Nigerian Colleges of Education — where course content today remains static PDFs, text pages, and conventional quizzes. With Lesson Studio, a Teacher supplies a topic and course context; the platform retrieves grounding material from the institution's corpus, generates a complete interactive lesson — slides, narration, quizzes, accurate labelled diagrams, interactive 3D models, and parameter-manipulable simulations — and hands it to the Teacher for review. Nothing reaches Students until the Teacher explicitly publishes it. Published lessons live inside Moodle courses, and quiz scores flow into the Moodle gradebook.

For time-poor subject experts with no prompt-engineering skill, this collapses weeks of content production into minutes of generation plus a focused review. For Students — including those on low-spec Android devices — it replaces static reading with interactive lessons grounded in their actual syllabus, plus on-demand labelled diagrams in the AI chat they already use. For institutions, it delivers this at unit economics that hold across large student populations: lessons are generated once, cached, and replayed at near-zero marginal cost.

The long-term vision is a fully immersive multi-agent AI classroom (streaming AI teacher, AI classmates, live Q&A, adaptive sequencing). None of that is in this PRD's scope; the MVP is built so that vision lands later as an *addition*, never a rewrite.

### 1.1 Load-Bearing Invariants

These four invariants fence every requirement in this document. They are non-negotiable; any change to them requires explicit stakeholder confirmation.

- **I-1 Generate-once economics.** Lessons are generated on Teacher request, cached, and replayed at near-zero marginal cost. No per-Student-per-session LLM inference exists in the MVP except the one deliberately cheap feature: on-demand Diagram Requests.
- **I-2 Review Gate.** No AI-generated content reaches Students without passing the Teacher review-and-publish gate — except sanitised on-demand SVG diagrams.
- **I-3 Schema-first.** The versioned Lesson Script Schema is the contract between generator, Player, and all future renderers. Published Versions remain playable forever.
- **I-4 Tenant isolation.** Every lesson, asset, cache, quota, log line, and query is Tenant-scoped. Cross-tenant access paths do not exist — including in internal/Operator tooling — outside explicit operator-role endpoints.

*Authoritative wording for these invariants: `project-context.md` §§1, 4, 6 [HARD].*

## 2. Target User

### 2.1 Jobs To Be Done

**Teachers (lecturers / teacher-trainers — primary authors; subject experts, moderate digital literacy, time-poor):**
- Turn my existing curriculum material into an interactive lesson without learning prompt engineering or authoring tools.
- Stay in control: review, correct, and approve everything before my students see it.
- Get lesson results into the gradebook I already use, without manual transfer.

**Students (pre-service teachers — primary consumers):**
- Learn from interactive, visual material that matches my actual syllabus, on the device I own.
- Check my understanding as I go and know my scores count.
- Get an accurate labelled diagram the moment I need one, inside the chat I already use.

**College administrators / sponsors (secondary):**
- Obtain evidence of usage and outcomes to justify the investment (MVP: event logging sufficient to build reporting later; no dashboard).

**Platform operator (internal):**
- Run ~60 institutions from one multi-tenant deployment with enforceable budgets, quotas, and API key hygiene, so cost and abuse are controlled per Tenant.

### 2.2 Non-Users (v1)

`[ASSUMPTION: inferred from the brief's deployment context (~60 institutions, Moodle-mediated access); the brief does not state a non-user list.]`

- Institutions outside the e-DON SIM PRO deployment; there is no self-serve sign-up.
- Users of LMS platforms other than Moodle (LTI 1.3 is explicitly deferred — §8).
- Independent teachers acting outside a Tenant institution.
- The general public; all access is mediated by institutional Moodle accounts.

### 2.3 Key User Journeys

*Captured from the brief's user descriptions; persona details are illustrative.* `[ASSUMPTION: persona names and situational details below are invented for concreteness; the roles, entry states, and paths come from the brief.]`

- **UJ-1. Dr. Amina generates, reviews, and publishes a lesson.**
  Dr. Amina, a physics education lecturer with 240 students and no time, opens her Moodle course and launches the Authoring UI from its teacher entry point — no separate login; the Course Context travels with her Launch Token (FR-29). She enters a topic ("Ohm's Law and simple circuits"), adds one line of guidance, and submits. The Generation Job is queued; she watches progress feedback. Under five minutes later a Draft is ready: slides, narration, a quiz, a circuit diagram, a 3D model Block, and a slider-driven simulation, each with Citations back to her institution's Corpus. She previews it exactly as Students will see it, fixes a misleading quiz distractor, deletes a redundant slide, reorders two Blocks, and publishes. The lesson becomes an immutable Published Version she places into her Moodle course. **Edge case:** the generated lesson is off-target; she discards the Draft, refines her guidance, and explicitly regenerates — the platform never regenerates on its own.

- **UJ-2. Chinedu completes a lesson on a budget Android phone.**
  Chinedu, a second-year pre-service teacher on a low-spec Android device, opens his Moodle course and taps the lesson activity. The Player loads the Published Version: he steps through slides with narration (browser speech synthesis), drags a simulation slider to see how current changes with resistance, and orbits a labelled 3D model. He answers the embedded quiz and gets immediate feedback; his score is written to the Moodle gradebook and his completion is tracked. **Edge case:** the 3D asset exceeds his device's budget; the Block degrades to its poster image and the lesson remains fully completable.

- **UJ-3. Ngozi requests a diagram in chat.**
  During revision, Ngozi, a first-year pre-service teacher, asks the existing AI chat for a labelled diagram of the human heart. The platform checks the Tenant-scoped cache, misses, generates an SVG grounded in the Tenant Corpus, sanitises it, caches it, and renders it — within her per-Student Rate Limit. A classmate requesting the same diagram minutes later gets the cached result instantly at zero LLM cost. **Edge case:** she exhausts her Rate Limit; the chat explains the limit clearly and when she can try again.

- **UJ-4. The Operator onboards a new college.**
  The platform operator creates a Tenant for a newly joining college, issues Tenant-scoped API credentials, and sets its LLM Budget Ceiling, generation Quota, diagram Quotas, and feature flags. From that point every lesson, asset, cache entry, log line, and quota for that college is isolated under its Tenant. `[ASSUMPTION: the operator surface is minimal (internal tooling, not a polished admin product); its form is an architecture decision.]` **Edge case:** a Tenant exhausts its monthly budget; generation queues pause with an explicit Teacher-facing notice, Diagram Requests degrade to cache-only with a clear message, and replay of Published Versions continues unaffected — silent failure is prohibited (stakeholder decision, OQ-9/OQ-1; I-1 keeps replay free).

- **UJ-5. Dr. Amina revises a published lesson.**
  A term later, Dr. Amina edits her lesson's Draft, improves two slides, and republishes. Republishing creates a new immutable Published Version; her Moodle activity serves the new version to Students starting it. `[ASSUMPTION: new Player sessions receive the latest Published Version; earlier versions remain stored and playable (I-3).]`

## 3. Glossary

*Downstream workflows must use these terms exactly. FRs, UJs, and SMs use Glossary terms verbatim.*

- **Tenant** — one institution (college) in the multi-tenant deployment (~60 at launch). Owns its Corpus, users, lessons, caches, quotas, budgets, and logs. All isolation is per-Tenant (I-4).
- **Teacher** — a lecturer / teacher-trainer at a Tenant; the primary author. (The brief's "lecturer" and "teacher-trainer" are this one term.)
- **Student** — a pre-service teacher enrolled in a Tenant's Moodle courses; the primary consumer.
- **Operator** — the internal platform operator managing Tenants, credentials, quotas, and budgets across the deployment.
- **Corpus** — a Tenant's curriculum document collection, indexed by the external edon-rag system. Retrieval returns **Grounding Chunks** — ranked excerpts with metadata.
- **Citation** — a stored link from generated lesson content back to the Grounding Chunk(s) it derives from.
- **Course Context / Course Reference** — the Moodle course a Lesson is generated for: recorded in the Lesson Script as the course reference, and the basis for course placement (FR-22) and grounding scope. Supplied exclusively by the Launch Token (FR-29); the platform never enumerates Moodle courses.
- **Curriculum Reference** — the curriculum/syllabus unit a Lesson addresses, recorded in Lesson Script metadata.
- **Lesson** — the authored unit: one topic, one course context, a version history of Drafts and Published Versions.
- **Lesson Script** — the JSON document conforming to the Lesson Script Schema that fully describes one version of a Lesson: metadata (Tenant, course reference, curriculum reference, version, Citations) plus an ordered list of Blocks.
- **Lesson Script Schema** — the versioned JSON schema (`"schema": "1.0"`) that is the contract between the generation pipeline, the Player, and all future renderers (I-3).
- **Block** — one unit of lesson content. MVP Block types: **Slide**, **Narration**, **Quiz**, **Diagram**, **Model3D**, **Simulation**.
- **Draft** — a generated or edited Lesson Script not visible to Students. Only Teachers interact with Drafts.
- **Published Version** — an immutable Lesson Script produced by an explicit publish action; the only Lesson content Students can ever receive (the I-2 diagram exception is chat content, not Lesson content). Republishing creates a new Published Version.
- **Review Gate** — the mandatory Teacher preview-edit-publish checkpoint between generation and Student visibility (I-2).
- **Generation Job** — one queued, asynchronous run of the generation pipeline producing a Draft, with progress feedback and cost telemetry.
- **Regeneration** — an explicit Teacher action that re-runs generation for a Lesson, or for a single Diagram, Model3D, or Simulation Block (FR-10; stakeholder decision, OQ-3). Never implicit.
- **Curated Model Library** — the internal, curriculum-mapped collection of openly licensed glTF 3D assets (with licence metadata) that generation selects and configures; AI never creates 3D geometry.
- **Diagram Request** — a Student-initiated request for a labelled SVG technical diagram, grounded in the Tenant Corpus, sanitised, cached, rate-limited, and quota-bound. The single per-interaction LLM feature in MVP (I-1). (Teacher-side diagrams arise as Diagram Blocks in the generation pipeline; Sanitisation covers both.)
- **Sanitisation** — the mandatory allowlist-based pass (e.g., stripping scripts, event handlers, `foreignObject`, external references — authoritative list: `project-context.md` §4 [HARD]) every LLM-derived SVG must survive before storage or rendering; failures are rejected, never passed through.
- **Player** — the JavaScript component that renders Published Versions for Students inside Moodle, and renders previews for Teachers.
- **Authoring UI** — the Teacher-facing web interface for initiating generation, reviewing, editing, and publishing. Reachable only via Moodle-initiated launch (FR-29) in MVP.
- **Launch Token** — the signed, short-lived credential minted when a Teacher launches the Authoring UI from mod_edonlesson, carrying Tenant, user ID, role, and course reference (FR-29). The sole source of Course Context.
- **Tenant Admin** — an institution-level role that may edit and republish any of its Tenant's Lessons; otherwise has Teacher capabilities (stakeholder decision, OQ-13).
- **mod_edonlesson** — the thin companion Moodle activity module (separate repository, GPLv3) that places Published Versions in courses, embeds the Player, and bridges completion and grades.
- **edon-rag** — the existing external production RAG backend providing Tenant-scoped retrieval. Accessed by API only; never modified by this product.
- **Quota** — a per-Tenant or per-user (Teacher or Student) cap on countable actions (e.g., Generation Jobs, Diagram Requests).
- **Rate Limit** — a temporal throttle (actions per time window) applied per user; distinct from a Quota (a countable cap). Guards LLM spend (FR-21, FR-26).
- **Budget Ceiling** — a per-Tenant monetary cap on LLM spend per calendar month, enforced by the platform (stakeholder decision, OQ-9).
- **Structured Event** — a logged, Tenant- and user-attributed record of a product action; the canonical event list lives in FR-27.
- **Cost Telemetry** — per-LLM-call structured records: tokens in/out, computed cost, Tenant, user, workload, cache hit/miss, latency (field list per `project-context.md` §3 [HARD]).

## 4. Features

*FRs are numbered globally (FR-1 … FR-29) with stable IDs. Each FR cites its source in the brief; requirements introduced or upgraded by the stakeholder decisions of 2026-07-07 cite that decision. Capabilities only — technology choices live in `project-context.md` and `addendum.md`.*

### 4.1 Lesson Script Schema (keystone)

**Description:** The versioned Lesson Script Schema is the product's spine (I-3): the generation pipeline writes it, the Player renders it, and every future renderer consumes it. It is a first-class deliverable, not an implementation detail — the brief designates it the keystone artifact. Realizes every UJ indirectly; UJ-2 and UJ-5 depend on its guarantees directly. *(Source: brief §6.)*

#### FR-1: Versioned lesson contract

The system defines Lesson Script Schema v1.0 (`"schema": "1.0"`) covering lesson metadata — Tenant, course reference, curriculum reference, version, Citations — and an ordered Block list with the six MVP Block types (Slide, Narration, Quiz, Diagram, Model3D, Simulation). *(Source: brief §6.)*

**Consequences (testable):**
- A Lesson Script missing the schema version, Tenant, or version metadata fails validation.
- Each of the six Block types has a schema definition strict enough that a conforming Player can render it without out-of-band knowledge.
- Citations are representable in the Lesson Script and survive publish unchanged.

#### FR-2: Forward compatibility

Schema versioning is explicit; Players ignore unknown Block types gracefully; Published Versions remain playable forever. *(Source: brief §6.)*

**Consequences (testable):**
- A Player given a Lesson Script containing an unrecognised Block type renders all other Blocks and completes the lesson without error.
- A v1.0 Published Version validates and plays after any later schema version ships; schema changes require a version bump and a documented migration/compatibility note. In MVP, "playable forever" is enforced by CI fixtures carrying unknown Block types and future version stamps.
- Version-mismatch behavior is defined: a Player encountering a newer minor version renders it, ignoring unknown fields and Blocks; a major-version mismatch yields a defined "cannot play this lesson" state — never silent corruption. `[ASSUMPTION: minor/major semantics to be ratified during schema design in architecture.]`

**Out of Scope:**
- Dialogue/agent-turn Block types, adaptive branching metadata, and streaming delivery are reserved for V3: not implemented, not precluded. `[NON-GOAL for MVP]`

#### FR-3: Shared validation and documentation

The Schema ships with validators and documentation, as a first-class package used by both the generation pipeline and the Player toolchain; no Lesson Script is persisted as a Draft without passing validation. *(Source: brief §6.)*

**Consequences (testable):**
- A non-conforming pipeline output is never stored as a Draft; the failure is visible to the Teacher as a failed Generation Job, never a silent gap.
- Backend and Player consume the same schema package (single source of truth).
- The package's documentation suffices for a renderer author to implement each Block type without reading pipeline code — demonstrated by the Player itself building every Block type against the schema package alone.

### 4.2 Lesson Generation

**Description:** A Teacher initiates generation from the Authoring UI with a topic, course context, and optional guidance. The platform retrieves Grounding Chunks from the Tenant's Corpus via the external edon-rag API, orchestrates LLM calls (lesson plan → per-Block content → validation), and persists a cited, schema-conforming Draft. Generation is asynchronous, cached, and never repeated implicitly (I-1). Realizes UJ-1. *(Source: brief §5 FR-A.)*

#### FR-4: Grounded generation request

A Teacher can initiate a Generation Job by supplying a topic, a course context, and optional free-text guidance; the pipeline retrieves Grounding Chunks from the Tenant's Corpus via the edon-rag retrieval API, scoped to that Tenant. Realizes UJ-1. *(Source: brief §5.1.)*

**Consequences (testable):**
- Every Generation Job retrieves exclusively from the requesting Teacher's Tenant Corpus (I-4).
- A request without a topic or course context is rejected with a clear message; guidance is optional.
- The Authoring UI requires no prompt-engineering skill: topic and guidance are plain fields; the Course Context is supplied by the Launch Token (FR-29), never typed or picked.

**Notes:** Authoring access is Moodle-initiated only (FR-29); the Course Context comes exclusively from the Launch Token — there is no course picker, and the platform never enumerates Moodle courses (stakeholder decision, OQ-11).

#### FR-5: Schema-conforming pipeline

The generation pipeline produces a validated, schema-conforming Lesson Script via a multi-stage pipeline. *(Source: brief §5.2; the brief's stage naming — lesson plan → per-Block content → validation — is preserved for the Architect in `addendum.md` §1.)*

**Consequences (testable):**
- Every persisted Draft passes FR-3 validation.
- A pipeline run whose output cannot be made conforming fails the Generation Job visibly (FR-8); it never stores a partial or invalid Draft.

#### FR-6: Citations stored

Every generated Lesson stores Citations linking its content back to the Grounding Chunks used. Citations are visible to the Teacher during review. *(Source: brief §5.3.)*

**Consequences (testable):**
- Every generated Draft carries at least one Citation. `[ASSUMPTION: a generation that retrieves no usable Grounding Chunks fails the Generation Job as ungrounded rather than producing an uncited lesson.]`
- Per-Block provenance is always stored — a data-model requirement. The Teacher review UI shows full per-Block Citations; the Student Player shows a Lesson-level "Sources" section only, with per-Block Student-facing display deferred to roadmap. (Stakeholder decision, OQ-10.)
- Teacher edits preserve Citations as provenance-of-generation (the product claim is "originally derived from the Corpus," not "every published word remains grounded after edits"); deleting a Block drops its Citations. (Stakeholder decision, OQ-10.)

#### FR-7: Draft persistence, caching, explicit regeneration

Generated Lessons persist as Drafts. Generation is idempotent and cached: resubmitting an identical request returns the existing Draft; Regeneration is an explicit Teacher action, never implicit. Realizes UJ-1 (edge case). *(Source: brief §5.4.)*

**Consequences (testable):**
- Submitting an identical generation request while a matching Draft exists does not invoke the LLM again. `[ASSUMPTION: idempotency is keyed on a normalised request (Tenant, course context, topic, guidance); exact normalisation is an architecture decision.]`
- No code path triggers Regeneration without an explicit Teacher action.
- Idempotency guards accidental resubmission only: an explicit Regeneration action always re-runs the pipeline, bypassing the idempotency cache.

#### FR-8: Asynchronous generation with progress

Generation Jobs are queued and processed asynchronously with progress feedback to the Teacher. *(Source: brief §5.5.)*

**Consequences (testable):**
- Initiating generation returns immediately; no API request blocks on a full generation run.
- The Teacher can observe job status through to completion or failure. `[ASSUMPTION: status states at minimum queued / in progress / complete / failed; finer-grained step progress is desirable but not committed.]`
- A failed Generation Job presents a Teacher-readable reason and leaves no Student-visible artifact.

### 4.3 Review and Publish (the Review Gate)

**Description:** The Review Gate (I-2) is the product's quality spine: every Draft passes through Teacher preview, optional editing, and an explicit publish action before any Student can see it. Publication produces an immutable Published Version; Drafts and Published Versions coexist; republishing creates a new version. Realizes UJ-1, UJ-5. *(Source: brief §5 FR-B.)* Ownership follows the creator-owns model (stakeholder decision, OQ-13): Drafts are private to their creator; Published Versions are visible Tenant-wide; any Teacher may duplicate a Published Version as a new Draft they own; editing and republishing are restricted to the owner plus the Tenant Admin role; no co-editing in MVP.

#### FR-9: Faithful preview

A Teacher can preview the full Draft exactly as Students will see it. Realizes UJ-1. *(Source: brief §5.6.)*

**Consequences (testable):**
- Preview and Student playback use the same Player rendering the same Lesson Script; publication does not alter the script the Teacher previewed (FR-11), so differences can arise only from device-dependent degradation states (FR-18).
- The Teacher can view each heavy Block's poster/fallback state in preview, so designed degraded states are reviewable. `[ASSUMPTION: fallback-state preview is a clarification of faithful preview, not new scope; confirm.]`
- All six Block types are previewable, including Simulation interaction.

#### FR-10: Block-level editing

A Teacher can edit Draft content at Block level: text edits, Block deletion, and Block reordering are required; Block-level Regeneration is required for Diagram, Model3D, and Simulation Blocks, while Slide and Quiz content relies on manual editing in MVP. *(Source: brief §5.7; regeneration commitment: stakeholder decision, OQ-3.)* Text edits apply to the text-bearing Block types — Slide, Narration, Quiz (including answers/feedback), and Model3D annotations; Diagram SVG and Simulation code are not content-editable, so Block-level Regeneration, deletion, and reordering are the Teacher's affordances there (approved editability map, A-28).

**Consequences (testable):**
- Text edits, deletion, and reordering of Blocks each produce a valid Draft (revalidated against the Schema).
- Regenerating a Diagram, Model3D, or Simulation Block replaces only that Block in the Draft and re-runs its validation (and, for Simulations, the FR-17 automated checks).
- Edits apply to Drafts only; no operation mutates a Published Version (FR-11).
- Only the Draft's creator (or a Tenant Admin) can edit, discard, or publish it (OQ-13); any Teacher may duplicate one of the Tenant's Published Versions as a new Draft they own.
- A Teacher can discard a Draft entirely; discard emits a Structured Event (FR-27). (Draft discard is implied by the brief's draft lifecycle and UJ-1; approved, A-28.)

**Notes:** Block-level Regeneration was upgraded from the brief's "desirable" to required for the three non-text-editable Block types by stakeholder decision (2026-07-07, OQ-3).

#### FR-11: Explicit, immutable publication

Publication is an explicit Teacher action producing an immutable Published Version. Drafts and Published Versions coexist; republishing creates a new Published Version. Realizes UJ-5. *(Source: brief §5.8.)*

**Consequences (testable):**
- No API or UI path mutates a Published Version.
- After republish, the prior Published Version still exists and remains playable (I-3); new Player sessions receive the latest Published Version. `[ASSUMPTION: "latest wins" for new sessions; in-flight sessions are not force-refreshed.]`

#### FR-12: Review Gate enforcement

Nothing is Student-visible until published. The only exception in MVP is sanitised on-demand Diagram Requests (Feature 4.5). *(Source: brief §5.9; invariant I-2.)*

**Consequences (testable):**
- Student-facing surfaces can retrieve Published Versions only; no Student-accessible path to Drafts exists.
- Attempted Student access to an unpublished Lesson yields a clear "not available" outcome, never Draft content.

### 4.4 Lesson Player

**Description:** A JavaScript Player renders Published Versions for Students inside Moodle pages and powers Teacher preview. It plays the ordered Block sequence — slides with narration, quizzes with immediate feedback, diagrams, interactive 3D models, and sandboxed simulations — and performs acceptably on low-spec Android devices. Realizes UJ-2. *(Source: brief §5 FR-C.)*

#### FR-13: Render all Block types

The Player renders a Published Version's full ordered Block sequence: Slide, Narration, Quiz, Diagram, Model3D, Simulation. Realizes UJ-2. *(Source: brief §5.10.)*

**Consequences (testable):**
- A Published Version containing all six Block types plays end to end.
- Block order in playback matches the Lesson Script's ordered list.

#### FR-14: Narration with a swappable provider

Narration in MVP uses the browser SpeechSynthesis API (no server-side TTS). The Player treats narration audio as a swappable provider so pre-generated or streaming neural TTS can plug in later without rework. *(Source: brief §5.11.)*

**Consequences (testable):**
- Narration plays via the browser's speech synthesis with no server-side audio generation or storage in MVP.
- On a device/browser without usable speech synthesis, narration degrades gracefully (lesson remains completable; narration text remains accessible). `[ASSUMPTION: narration content is available as on-screen text when audio is unavailable.]`

#### FR-15: Quiz Blocks — instant client feedback, server-authoritative scoring

Quiz Blocks support at minimum multiple-choice and short-answer questions with defined answers and feedback. Client-side scoring against the Published Version gives the Student instant feedback; the server re-scores every submitted answer deterministically against the same Published Version before any gradebook writeback — the server score is authoritative. Realizes UJ-2. *(Source: brief §5.12; server-authoritative re-scoring: stakeholder decision, OQ-14.)*

**Consequences (testable):**
- Multiple-choice and short-answer questions give instant client-side feedback without a server round-trip.
- Short-answer scoring is deterministic: normalised matching (case/whitespace/punctuation) against Teacher-approved accepted-answer lists, editable during review (FR-10). No LLM-based answer judging in MVP (I-1). (Stakeholder decision, OQ-4.)
- The server re-scores every submission; only the server score reaches the backend record and Moodle (FR-23) — a client-asserted score never writes to the gradebook.
- Each scored quiz submission produces a Structured Event and a grade report (FR-23).

#### FR-16: 3D model Blocks from the Curated Model Library

Model3D Blocks render curated glTF assets in an interactive viewer with orbit/zoom and authored annotations. Assets come exclusively from the Curated Model Library (manually seeded in MVP); generation *selects and configures* models — it never generates 3D geometry. *(Source: brief §5.13, §8.4.)*

**Consequences (testable):**
- Every Model3D Block references a Curated Model Library asset carrying licence and attribution metadata.
- Orbit and zoom work on supported devices; authored annotations display as configured in the Lesson Script.
- No pipeline path creates 3D geometry.

#### FR-17: Simulation Blocks, sandboxed

Simulation Blocks run in sandboxed iframes — no network access, no storage APIs, strict content-security policy, communication only via a defined postMessage protocol — and expose authored manipulable parameters (sliders/inputs) to Students. Simulation code is produced during Teacher-initiated generation and must pass the Review Gate plus automated checks before publish. Realizes UJ-2. *(Source: brief §5.14.)*

**Consequences (testable):**
- A Simulation Block cannot reach the network, parent page (beyond the defined protocol), or storage APIs from inside its sandbox.
- Manipulating an authored parameter changes the simulation live for the Student.
- A Simulation that fails automated pre-publish checks blocks publication of that Draft with a Teacher-readable reason. `[ASSUMPTION: the check failure blocks publish rather than silently dropping the Block; the Teacher can delete the Block (FR-10) to proceed.]`
- The automated pre-publish checks verify, at minimum: the Simulation loads without runtime error inside the sandbox, respects the postMessage protocol, exposes its authored parameters, and stays within its resource budget. Mechanism per architecture. `[ASSUMPTION: minimum check intent — extend in architecture, do not narrow.]`

#### FR-18: Low-spec device performance

The Player performs acceptably on low-spec Android devices. Heavy assets are compressed and size-budgeted per Block, with a poster-image fallback so lessons degrade gracefully rather than fail. Realizes UJ-2 (edge case). *(Source: brief §5.15.)*

**Consequences (testable):**
- The reference device floor is a mixed fleet including very old devices: ~1.5–2 GB RAM, Android 8-era hardware, and potentially outdated WebViews. (Stakeholder decision, OQ-16.)
- Every Model3D asset satisfies a per-Block size budget (values set in architecture) and ships compressed; the Player itself ships under a strict bundle-size budget (value set in architecture, enforced in CI).
- The poster-image fallback is a required first-class path for Model3D and Simulation Blocks, including no-WebGL environments; when a heavy Block cannot run, its poster displays and the lesson remains fully completable, including its Quiz Blocks.
- The CI low-spec profile applies aggressive CPU/memory throttling (per `project-context.md` §7).

### 4.5 Student On-Demand Diagram Generation

**Description:** The single per-interaction LLM feature in MVP (I-1): Students request accurate labelled technical diagrams from within the existing AI chat, grounded in the Tenant Corpus, generated as SVG, sanitised, cached, rate-limited, and quota-bound. This is also the only exception to the Review Gate (I-2), which is why Sanitisation is mandatory and absolute. Realizes UJ-3. *(Source: brief §5 FR-D.)*

#### FR-19: Grounded diagram requests in chat

A Student can request a labelled technical diagram (rendered as SVG) from within the existing AI chat experience, grounded in the Tenant Corpus. Realizes UJ-3. *(Source: brief §5.16; the intermediate-representation note moved to `addendum.md` §1.)*

**Consequences (testable):**
- Diagram generation is grounded: retrieval is scoped to the requesting Student's Tenant (I-4), and the diagram prompt always includes retrieved Grounding Chunks — ungrounded generation is not a fallback (FR-28).
- Diagram Requests are identity-stripped before the adapter call: no Student personal identifiers appear in any prompt or request sent to the external LLM provider (NFR-9).
- The result renders as a labelled SVG inside the existing chat surface.

**Notes:** The chat surface is the existing block_edon_ai plugin — a modifiable companion (stakeholder decision, OQ-12) with a minimal surface: it calls the platform diagram endpoint and renders the already-sanitised SVG returned; Sanitisation, caching, Quotas, and identity-stripping remain server-side.

#### FR-20: Mandatory Sanitisation

Every SVG derived from LLM output — whether emitted directly or produced from an LLM-emitted intermediate representation, Student- or Teacher-side — passes the allowlist-based Sanitisation before storage or rendering. Failures reject the output; nothing passes through raw. *(Source: brief §5.17; `project-context.md` §4 [HARD].)*

**Consequences (testable):**
- No SVG reaching storage or a rendering surface contains a script, event handler, `foreignObject`, or external reference: disallowed constructs are stripped by the allowlist pass, and an SVG that cannot be made conforming is rejected outright.
- A Sanitisation failure produces a clear user-facing "couldn't produce that diagram" outcome and a Structured Event; it never renders partial unsanitised content.

#### FR-21: Diagram caching, rate limits, and quotas

Diagram Requests are cached Tenant-scoped on a normalised request key *before* any LLM call, rate-limited per Student, and bounded by per-Tenant Quotas. Realizes UJ-3 (edge case). *(Source: brief §5.18.)*

**Consequences (testable):**
- A repeated equivalent Diagram Request within a Tenant is served from cache with no LLM call.
- A Student exceeding their Rate Limit receives a clear message stating when they can retry; a Tenant at Quota stops incurring diagram LLM spend.
- Cache hits and misses are recorded in Cost Telemetry (FR-27).
- Rate Limits guard LLM spend: cache hits do not count against a Student's Rate Limit. (Stakeholder decision, OQ-2; diagram Quota default 20/Student/day, tunable config.)

#### FR-28: Diagram accuracy governance

Because the diagram channel bypasses the Review Gate (I-2), it carries its own governance bundle: mandatory Corpus grounding in the diagram prompt, a visible AI-content label, a Student report control feeding a Teacher review queue, and telemetry-sampled spot checks. *(Stakeholder decision, 2026-07-07 — OQ-17.)*

**Consequences (testable):**
- Every rendered diagram displays a visible "AI-generated — verify against your course materials" label.
- A Student can report/flag a diagram; the report emits a Structured Event (FR-27) and enqueues the diagram for Teacher review.
- Spot checks are supported by sampling diagram Structured Events and Cost Telemetry; they require no additional Student-facing surface.

### 4.6 Moodle Integration

**Description:** A thin companion Moodle activity module, mod_edonlesson (separate repository, GPLv3 as Moodle requires; all proprietary logic stays server-side), lets Teachers place Published Versions into courses and embeds the Player for Students. Completion flows to Moodle completion tracking; quiz scores flow to the Moodle gradebook. Realizes UJ-1, UJ-2. *(Source: brief §5 FR-E.)*

#### FR-22: Course placement and embedded playback

A Teacher can place a Published Version into a Moodle course via mod_edonlesson; Students launch it there and the module embeds the Player. *(Source: brief §5.19.)*

**Consequences (testable):**
- A published Lesson is placeable as a course activity by a Teacher with normal Moodle course-editing rights and no platform-side help.
- The Player runs embedded in the Moodle page (no redirect to an external site for lesson playback). `[ASSUMPTION: same-page embedding; pop-out is not required.]`
- mod_edonlesson contains no proprietary platform logic (thin client of the platform API).

#### FR-23: Completion and gradebook writeback

mod_edonlesson reports lesson completion to Moodle completion tracking and writes quiz scores to the Moodle gradebook via Moodle's grade APIs. Realizes UJ-2. *(Source: brief §5.20.)*

**Consequences (testable):**
- For 100% of Published Versions placed in courses, completion and quiz-score writeback function (SM-3); the score written is the server-authoritative one (FR-15).
- A Student's quiz score appears in the course gradebook attributed to the correct Student.
- Writeback failures are logged as Structured Events and are retriable without Student rework. `[ASSUMPTION: retry-on-failure is required behavior; mechanism is an architecture decision.]`
- Lifecycle semantics (stakeholder decision, OQ-15): completion fires when the Student has viewed every Block and submitted every Quiz Block; retakes are allowed with Teacher-configurable attempt limits; the gradebook records the highest attempt; completions and grades stay pinned to the Published Version the Student took, and new attempts use the latest Published Version. Resume-after-disconnect behavior remains an architecture decision.

#### FR-24: Tenant-scoped authentication and identity attribution

Authentication between mod_edonlesson and the platform uses Tenant-scoped credentials consistent with the existing block_edon_ai (the deployed Moodle AI-chat plugin) / edon-rag pattern; Student identity passes through so results attribute correctly. *(Source: brief §5.21.)*

**Consequences (testable):**
- Each Tenant's Moodle instance authenticates with credentials valid only for that Tenant (I-4).
- Grade and completion records attribute to the correct Moodle user identity.

#### FR-29: Moodle-initiated Authoring launch

Authoring access is Moodle-initiated only in MVP: a teacher-facing entry point in mod_edonlesson launches the Authoring UI with a signed, short-lived Launch Token carrying Tenant, user ID, role, and course reference. Course Context comes exclusively from the Launch Token; there is no standalone login. Realizes UJ-1. *(Stakeholder decision, 2026-07-07 — OQ-11.)*

**Consequences (testable):**
- The Authoring UI is reachable only with a valid Launch Token; an expired or tampered token yields a clear "relaunch from Moodle" outcome, never partial access.
- The platform never enumerates Moodle courses; the course reference on every Generation Job equals the one carried by the launching token (FR-4).
- Standalone (non-Moodle) authentication for the Authoring UI is out of scope for MVP (§8). `[NON-GOAL for MVP]`

### 4.7 Multi-Tenancy, Administration, and Cost Control

**Description:** One deployment serves ~60 Tenants with full isolation (I-4), per-Tenant configuration, and the event and cost instrumentation that keeps the economics honest (I-1) and powers future reporting. Realizes UJ-4. *(Source: brief §5 FR-F.)*

#### FR-25: Full Tenant isolation

Lessons, assets, caches, Quotas, Budget Ceilings, and logs are isolated per Tenant, consistent with the existing edon-rag multi-tenant model. *(Source: brief §5.22.)*

**Consequences (testable):**
- No query, cache key, asset path, log line, or quota check crosses Tenants; no cross-Tenant access path exists — including in internal/Operator tooling — outside explicit Operator-role endpoints (`project-context.md` §4 [HARD]).
- A Teacher or Student at Tenant A can never retrieve Tenant B's Lessons, Diagram cache entries, or assets.

#### FR-26: Per-Tenant configuration

The Operator can configure, per Tenant: LLM Budget Ceilings, generation Quotas, diagram Quotas, per-user Rate Limits, and feature flags. Realizes UJ-4. *(Source: brief §5.23.)* Per-user Rate Limits ship as platform defaults overridable per Tenant (stakeholder decision, OQ-2).

**Consequences (testable):**
- Budget and Quota enforcement is effective at the platform layer, not merely reflected in UI (per `project-context.md` §4).
- Configuration defaults are tunable config, not code (stakeholder decision, OQ-1/OQ-2): soft alert at $2 per Lesson generation; per-Tenant monthly LLM budget set by the Operator; diagram Quota default 20/Student/day.
- When a Tenant's Budget Ceiling is exhausted, generation queues pause with an explicit Teacher-facing notice and Diagram Requests degrade to cache-only with a clear user-facing message; replay of Published Versions is never blocked; silent failure is prohibited. (Stakeholder decision, OQ-9; I-1.)
- Feature flags can disable a Block type or the Diagram feature for a Tenant. `[ASSUMPTION: flag granularity includes at least the Diagram feature and Simulation Blocks, and toggling takes effect without redeploying; the brief specifies only "feature flags" — exact set and mechanism are architecture decisions.]`
- Per-user Rate Limits are enforceable at the platform layer for all LLM-spending actions — not only Diagram Requests — so a single Teacher cannot exhaust a Tenant's Budget Ceiling unthrottled (`project-context.md` §4).
- A Generation Job already in flight when the Budget Ceiling is crossed runs to completion (bounded overrun of at most one job); a failed job's real LLM spend still counts against the Budget. (Approved, A-29.)

#### FR-27: Structured Events and Cost Telemetry

The platform logs Structured Events — lesson generated / generation failed / draft discarded / published / started / completed, quiz submitted, diagram requested / diagram served from cache / diagram reported / diagram review completed / diagram invalidated (cache evicted), Sanitisation failure, Rate Limit or Quota rejection, writeback failure and retry, writeback overdue, operator action, cost alert *(the last five ratified as taxonomy extensions at architecture sign-off, 2026-07-18; spine AD-7 is the canonical list)* — sufficient to power a future analytics dashboard, and Cost Telemetry on every LLM call: tokens in/out, computed cost, Tenant, user, workload, cache hit/miss, latency. All logs carry Tenant and user identifiers (a known gap in existing edon-rag query logs; not repeated here). *(Source: brief §5.24; `project-context.md` §3 [HARD].)* `[ASSUMPTION: this event list is canonical and extends the brief's six events with the failure/rejection events the PRD's own FRs and metrics require (FR-10, FR-20, FR-23, SM-2, SM-C3).]`

**Consequences (testable):**
- Every listed product action emits a Structured Event with Tenant and user identifiers; this FR's event list is the single canonical taxonomy — an event referenced anywhere in this PRD appears here.
- Every LLM call emits Cost Telemetry; per-Tenant and per-Lesson cost is computable from stored telemetry alone (makes SM-4 and SM-5 computable).
- Diagram cache hits are additionally recorded as zero-cost telemetry events (no token fields), so cache hit rate (SM-5) is computable without diluting the per-LLM-call definition.
- Student identifiers in telemetry are pseudonymised where feasible while preserving the [HARD] Tenant/user attribution requirement (NFR-9; `project-context.md` §§3–4).
- No analytics dashboard UI is built in MVP. `[NON-GOAL for MVP]`

## 5. Cross-Cutting NFRs

- **NFR-1 Performance (generation):** median time from Teacher initiation to "Draft ready for review" under 5 minutes (SM-1).
- **NFR-2 Performance (playback):** the Player is usable on low-spec Android hardware; heavy Block types carry per-Block asset size budgets and compressed assets, with poster fallbacks (FR-18). Low-spec behavior is continuously exercised in automated testing (`project-context.md` §7). Reference floor (stakeholder decision, OQ-16): a mixed fleet including ~1.5–2 GB RAM, Android 8-era devices with potentially outdated WebViews — encoded as a strict Player bundle-size budget, required poster fallbacks for Model3D/Simulation including no-WebGL environments, and an aggressively throttled CI low-spec profile (FR-18).
- **NFR-3 Security:** allowlist SVG Sanitisation (FR-20); Simulation iframe sandboxing with strict CSP and no network (FR-17); Tenant isolation everywhere (FR-25); no wildcard CORS — allowed origins are per-Tenant configuration; secrets via environment configuration only; API key rotation (issue/revoke without downtime) from day one. *(Source: brief §9; `project-context.md` §4 [HARD].)*
- **NFR-4 Reliability and durability:** Published Versions remain playable forever (I-3); lesson replay does not depend on LLM provider availability; a failed Generation Job never corrupts an existing Draft or Published Version.
- **NFR-5 Observability:** structured, Tenant- and user-attributed logging throughout; Cost Telemetry (FR-27) is the instrument for all future model-migration decisions (`project-context.md` §3).
- **NFR-6 Cost discipline:** the generate-once invariant (I-1) is a system property, not a guideline — no MVP design introduces per-Student-per-session inference beyond Diagram Requests.
- **NFR-7 Legal and licensing:** clean-room constraint — no code copied, ported, or adapted from OpenMAIC (AGPL-3.0) or any copyleft codebase; platform dependencies are permissively licensed; mod_edonlesson is GPLv3 and thin; every Curated Model Library asset stores licence and attribution metadata. *(Source: brief §9; `project-context.md` §5 [HARD].)*
- **NFR-8 Localisation-readiness:** English-language content at launch. Localisation-ready means, testably: no user-facing string is hardcoded in Authoring UI or Player chrome (strings externalised), and Lesson Script text fields carry a language tag. Localisation of generated lesson content is roadmap, not MVP. *(Source: brief §11.)*
- **NFR-9 Data protection (stakeholder decision, OQ-8):** (a) no Student personal identifiers in any prompt or request sent to external LLM providers — Diagram Requests are identity-stripped before the adapter call (FR-19); (b) Student identifiers in telemetry are pseudonymised where feasible, preserving the [HARD] Tenant/user attribution requirement (`project-context.md` §§3–4); (c) log retention is a defined, configurable period, default 12 months; (d) a maintained record of external processors exists. The full NDPA compliance programme is platform-level and out of PRD scope.

## 6. Integrations and External Dependencies

This is a greenfield build in a new repository. The systems below are external dependencies accessed only via APIs; their source is not assumed available, and required contract gaps become integration work items — never edits to the external systems. *(Source: brief §8; contract expectations for the Architect are preserved in `addendum.md`.)*

- **edon-rag** (existing production RAG backend) — Tenant-scoped retrieval of Grounding Chunks with metadata/Citations, for lesson generation (FR-4) and Diagram Requests (FR-19).
- **Moodle 5.x** (existing production LMS) — integration exclusively through mod_edonlesson and Moodle's own grade, completion, and web-service APIs (FR-22–FR-24).
- **LLM provider** — all model access via a provider-agnostic adapter with per-workload configuration; no hardcoded model identifiers (`project-context.md` §3 [HARD]).
- **3D asset sources** — openly licensed collections (e.g., Smithsonian 3D, NIH 3D) seed the Curated Model Library; licence metadata stored per asset (FR-16).
- **block_edon_ai** (existing production Moodle AI-chat plugin) — the chat surface that hosts Diagram Requests (FR-19). A modifiable companion owned by the team (stakeholder decision, OQ-12): its enhancement is a registered third-repository work item with a minimal surface — call the platform diagram endpoint and render the already-sanitised SVG it returns; Sanitisation, caching, Quotas, and identity-stripping stay server-side (`addendum.md` §2).

## 7. Constraints and Guardrails

- **Safety:** the Review Gate (I-2, FR-12) is the content-safety mechanism for all lesson content; Sanitisation (FR-20) and Simulation sandboxing (FR-17) cover the two channels that bypass or execute beyond it.
- **Privacy:** the platform receives Student identity from Moodle solely for grade/completion attribution (FR-24) and event attribution (FR-27), and stores the minimum Student identifiers needed for attribution and no additional Student PII (A-15, approved). Data-protection requirements are NFR-9 (stakeholder decision, OQ-8); the full NDPA programme is platform-level, out of PRD scope.
- **Cost:** per-Tenant Budget Ceilings and Quotas (FR-26), pre-LLM cache checks (FR-21, FR-7), and Cost Telemetry (FR-27) operationalise I-1.
- **Legal:** clean-room and licensing rules per NFR-7; these are [HARD] rules in `project-context.md` and bind every downstream workflow.

## 8. Non-Goals (Explicit)

The MVP is not, and does not include *(source: brief §7 — the PM must not promote these into MVP)*:

- **No server-side or neural TTS** — narration is browser speech synthesis behind a provider seam (FR-14).
- **No multi-agent classroom features of any kind** — no AI teacher persona, AI classmates, live Q&A, or adaptive sequencing.
- **No Student-triggered Simulation generation** — Simulations are created only during Teacher-initiated generation.
- **No cross-Tenant lesson sharing or library.**
- **No analytics dashboard UI** — events are logged (FR-27); reporting is future work.
- **No offline/SCORM export** — designed-for but not built; schema and static-asset discipline must keep it a cheap fast-follow. `[NOTE FOR PM]` The brief marks this designed-for; promotion into MVP requires explicit stakeholder confirmation (brief §12.2).
- **No LTI 1.3 / non-Moodle LMS support.**
- **No AI illustrative image generation** (diagrams are SVG only).
- **No text-to-3D generation** — Model3D Blocks use the Curated Model Library only (FR-16).
- **No standalone (non-Moodle) authentication for the Authoring UI** — access is Moodle-initiated via Launch Token only (FR-29; stakeholder decision, OQ-11).

And by invariant:
- **No per-Student-per-session LLM inference** beyond Diagram Requests (I-1).
- **No AI content bypassing the Review Gate** beyond sanitised diagrams (I-2).
- **No modification of external systems** — edon-rag and Moodle core are consumed via API only (§6). (block_edon_ai is a modifiable companion by stakeholder decision, OQ-12 — see §6.)

## 9. MVP Scope

### 9.1 In Scope

- Lesson Script Schema v1.0 as a first-class shared package — schema, validators, documentation (Feature 4.1).
- Teacher-initiated, corpus-grounded, asynchronous lesson generation with Citations, caching, and explicit Regeneration (Feature 4.2).
- Teacher Review Gate: faithful preview, Block-level editing and Regeneration (Diagram/Model3D/Simulation), creator-owned Drafts with Tenant Admin override, explicit immutable publication with versioning (Feature 4.3).
- Embeddable Player for all six Block types with browser-based narration, instant-feedback quizzes with server-authoritative scoring, curated 3D, sandboxed Simulations, and low-spec device discipline (Feature 4.4).
- Student on-demand Diagram Requests in the existing chat: grounded, sanitised, cached, rate-limited, quota-bound, with accuracy governance — labelling, Student reporting, spot checks (Feature 4.5).
- mod_edonlesson Moodle module: course placement, embedded playback, completion tracking, gradebook writeback, Tenant-scoped auth, and the Moodle-initiated Authoring launch (Feature 4.6).
- Multi-tenancy for ~60 Tenants with isolation, per-Tenant budgets/quotas/flags, Structured Events, and Cost Telemetry (Feature 4.7).

### 9.2 Out of Scope for MVP

Everything in §8, unchanged. Deferral horizons per the brief: multi-agent classroom capabilities, streaming delivery, and adaptive sequencing are V3 roadmap; offline/SCORM export and neural TTS are designed-for fast-follows; the analytics dashboard builds on MVP event logging when prioritised. No §7 brief item may enter MVP without explicit stakeholder confirmation.

## 10. Success Metrics

*Targets from brief §4. Each SM names the FRs it validates; counter-metrics are as load-bearing as primaries.*

**Primary**
- **SM-1**: Median time from Teacher initiation to "Draft ready for review" — **under 5 minutes**. The clock starts at request submission (queue time included); p90 is tracked alongside the median. Validates FR-5, FR-8. (Approved, A-34: provisional p90 target of 2× the median bar.)
- **SM-2**: Share of generated Lessons reaching a Published Version — **≥ 70%** (generation-quality proxy: if Teachers discard most Drafts, generation is failing). Measured per Lesson over a rolling 30-day window: a Lesson counts as successful once any of its Generation Jobs yields a Published Version; median Generation Jobs per Published Version is tracked alongside so per-Lesson counting cannot hide churn. Validates FR-4–FR-10. (Denominator definition approved, A-23.)
- **SM-3**: Completion tracking and quiz-score writeback functioning for **100% of Published Versions** placed in courses — meaning every completion and quiz score is durably recorded, with retries (FR-23), within a defined window. Validates FR-15, FR-22–FR-24. (24-hour eventual-consistency window approved, A-25.)
- **SM-4**: Fully-loaded generation cost per Lesson **below the soft-alert threshold of $2** (a tunable config default — stakeholder decision, OQ-1). "Fully-loaded" counts all Generation-Job LLM spend attributable to the Lesson — including failed jobs and Regenerations — divided by its Published Versions (approved, A-24). The near-zero-replay claim is structural, not measured: the replay path contains zero LLM calls, verified as such. Validates FR-7, FR-27; computed from Cost Telemetry alone.

**Secondary**
- **SM-5**: Diagram Requests served at low per-request cost — governed as tunable config via the mini-tier model, Tenant budgets, and the 20/Student/day Quota default (stakeholder decision, OQ-2) — with cache hit rate tracked and rising as the cache warms. Validates FR-21, FR-27, FR-28.

**Counter-metrics (do not optimize)**
*(A PM addition beyond brief §4, carried per PRD discipline; approved by stakeholder, A-17. Provisional triggers approved, A-32.)*
- **SM-C1**: Median time-to-publish (lesson-generated → published Structured Events). Named honestly: this measures calendar delay, not review effort — a true review-effort signal would need review-session instrumentation, a potential scope addition requiring stakeholder confirmation. Watch for the median collapsing toward zero, the rubber-stamp signal. Counterbalances SM-1, SM-2. `[ASSUMPTION: provisional trigger — review the Review Gate's health if the median falls below 5 minutes.]`
- **SM-C2**: Block-type richness of Published Versions (share containing interactive Blocks — Quiz, Model3D, Simulation). Publish rate must not be achieved by generating impoverished slide-only lessons. Counterbalances SM-2. `[ASSUMPTION: provisional trigger — review if the interactive share falls below 60%.]`
- **SM-C3**: Student Diagram Request denial rate (Rate Limit/Quota rejection events, FR-27). Diagram cost must not be controlled by throttling Students out of a headline feature. Counterbalances SM-4, SM-5. `[ASSUMPTION: provisional trigger — review if weekly denials exceed 10% of Diagram Requests.]`

## 11. Risks and Mitigations

*(Source: brief §11; carried so downstream workflows inherit them.)*

- **Generation quality** may need significant iteration before SM-2's 70% is met. Mitigation: the Review Gate absorbs variance; the pipeline is tunable configuration, not code constants.
- **Simulation safety/quality** is the highest-variance MVP feature. Mitigation: sandbox + automated checks + mandatory preview; if quality is poor at MVP, ship a small library of parameterised simulation templates the generator configures instead of free-coding — architecture must let both modes coexist (decision point: OQ-5).
- **Device performance** for 3D and Simulations on low-spec hardware. Mitigation: asset budgets, compression, poster-image degradation (FR-18).
- **Cost creep.** Mitigation: per-Tenant budgets (FR-26), Cost Telemetry per call (FR-27), caching discipline (FR-7, FR-21).
- **Grade integrity (mitigated).** Client-side scoring provides instant feedback, and defined answers necessarily ship to the Student device — answer extraction remains possible and is accepted, with quizzes treated as formative-stakes (A-21) and Teacher-configurable attempt limits (FR-23). Score forgery is closed: the server re-scores every submission and is authoritative for gradebook writeback (FR-15; stakeholder decision, OQ-14).
- **Narration availability.** Browser speech-synthesis support is patchy on exactly the low-spec Android class the product targets — narration may effectively be on-screen text for much of the Student population. Mitigation: graceful degradation with narration text accessible (FR-14, A-9); stated here so it is a known experience fact, not a discovery.
- **Assumptions inherited from the brief:** edon-rag retrieval quality suffices for grounding (validated by existing chat usage); institutional bandwidth suffices for online delivery; English-only content at launch (NFR-8).

## 12. Open Questions and Resolutions

*Stakeholder decisions dated 2026-07-07 resolved OQ-1–OQ-4 and OQ-8–OQ-17; the requirements they produced are folded into §§3–11 and marked "stakeholder decision". One-line records below preserve the OQ IDs downstream references use; the full decision text is in `.memlog.md`. The remaining four (OQ-5/6/7/18) were resolved in the UX and architecture phases — pointers below, updated 2026-07-18.*

**Resolved (stakeholder decisions, 2026-07-07)**
1. **OQ-1 — RESOLVED:** cost governance as tunable config: $2 soft-alert per Lesson generation; per-Tenant monthly budgets Operator-set (SM-4, FR-26). Cost-attribution (A-24), p90/concurrency (A-34), and counter-metric triggers (A-32) approved.
2. **OQ-2 — RESOLVED:** diagram Quota default 20/Student/day (tunable config); per-user Rate Limits as platform defaults overridable per Tenant; cache hits exempt from Rate Limits (FR-21, FR-26). No PRD-level latency SLA; per-request cost governed by the mini-tier model plus budgets.
3. **OQ-3 — RESOLVED:** Block-level Regeneration committed to MVP for Diagram, Model3D, and Simulation Blocks; Slide/Quiz content relies on manual editing (FR-10).
4. **OQ-4 — RESOLVED:** deterministic short-answer scoring only — normalised matching (case/whitespace/punctuation) against Teacher-approved accepted-answer lists, editable during review; no LLM judging (FR-15).
5. **OQ-8 — RESOLVED:** data-protection NFR added (NFR-9): identity-stripped LLM requests, pseudonymised telemetry where feasible, configurable log retention (default 12 months), record of external processors. Full NDPA programme is platform-level.
6. **OQ-9 — RESOLVED:** calendar-month budgets; on exhaustion, generation queues pause with explicit notice and Diagram Requests degrade to cache-only; replay never blocked; silent failure prohibited (FR-26).
7. **OQ-10 — RESOLVED:** per-Block provenance always stored (data-model requirement); Teacher review shows full per-Block Citations; Student Player shows a Lesson-level "Sources" section only, per-Block Student display deferred to roadmap (FR-6).
8. **OQ-11 — RESOLVED:** Moodle-initiated launch only — teacher entry point in mod_edonlesson passes a signed, short-lived Launch Token (Tenant, user ID, role, course ID); Course Context comes exclusively from the token; no standalone login in MVP; the platform never enumerates Moodle courses (FR-29, §8).
9. **OQ-12 — RESOLVED:** block_edon_ai is ours and modifiable — registered third-repository work item with minimal surface: call the platform diagram endpoint, render the returned sanitised SVG; all logic server-side (§6; `addendum.md` §2).
10. **OQ-13 — RESOLVED:** creator-owns model — Drafts private to their creator; Published Versions visible Tenant-wide and duplicable by any Teacher as a new owned Draft; edit/republish restricted to owner + Tenant Admin; no co-editing in MVP (§4.3, FR-10).
11. **OQ-14 — RESOLVED:** forgeable client grades rejected — client-side scoring is instant feedback only; the server re-scores deterministically against the Published Version before any gradebook writeback and is authoritative (FR-15, FR-23).
12. **OQ-15 — RESOLVED:** A-22 defaults made explicit — completion = all Blocks viewed + all quizzes submitted; retakes with Teacher-configurable attempt limits; gradebook records the highest attempt; completions/grades pinned to the version taken; new attempts use the latest Published Version (FR-23).
13. **OQ-16 — RESOLVED:** device floor — mixed fleet including ~1.5–2 GB RAM, Android 8-era hardware, outdated WebViews; encoded as strict Player bundle-size budget, required poster fallback (Model3D/Simulation, including no-WebGL), aggressively throttled CI low-spec profile (FR-18, NFR-2).
14. **OQ-17 — RESOLVED:** diagram governance bundle accepted — mandatory grounding in the prompt, visible "AI-generated — verify against your course materials" label, Student report/flag control feeding a Teacher review queue, telemetry-sampled spot checks (FR-28).

**Resolved in later phases (pointers added 2026-07-18 — all 18 OQs now closed)**
15. **OQ-5 — RESOLVED (architecture sign-off, 2026-07-18):** dual-mode Simulation schema (`template | freecode`, one sandbox + protocol); **template library is the launch default regardless of benchmark outcome**; free-code activates behind a tenant flag only after clearing the ≥ 70% automated-check gate (ADR-002/ADR-007); the template seed set is a first-class deliverable.
16. **OQ-6 — RESOLVED (stakeholder, 2026-07-18):** Model3D stories are blocked until a curated seed library of ≥ 20 models across 2–3 NCE science subjects exists; the stakeholder is the initial curator; licence metadata mandatory (`project-context.md` §5).
17. **OQ-7 — RESOLVED (UX ruling, 2026-07-17):** WCAG 2.1 AA adopted, scoped — full AA on controlled surfaces; AI-generated content governed by the text-alternative contract + best-effort (EXPERIENCE.md § Rulings & Open Items, item 1).
18. **OQ-18 — RESOLVED (stakeholder, 2026-07-18):** adoption metric adopted — **% of Published lessons with ≥ 1 Student completion within 30 days of publication**, computed from existing FR-27 events; no new instrumentation.

*Note (2026-07-18): the OQ-16 device-floor ruling is superseded in part by the stakeholder realignment recorded in `addendum.md` §5 — modern-device canonical posture; the floor becomes best-effort fallback.*

## 13. Assumptions Index

*Approved by the stakeholder on 2026-07-07: A-1–A-35 stand as accepted defaults. Entries refined or superseded by the §12 OQ decisions are updated below to their decided form; remaining inline `[ASSUMPTION]` tags mark where an approved default lives in the text.*

- **A-1** (§2.3 UJ-1–UJ-5): persona names and situational details are invented; roles and paths come from the brief.
- **A-2** (§2.3 UJ-4): the Operator surface is minimal internal tooling; its form is an architecture decision.
- **A-3** (§2.3 UJ-4, §4.7 FR-26): budget exhaustion pauses generation queues with explicit notice and degrades Diagram Requests to cache-only; replay is never blocked; silent failure prohibited (resolved, OQ-9).
- **A-4** (§2.3 UJ-5, §4.3 FR-11): new Player sessions receive the latest Published Version; earlier versions remain stored and playable; in-flight sessions are not force-refreshed.
- **A-5** (§4.2 FR-6): a generation retrieving no usable Grounding Chunks fails as ungrounded rather than producing an uncited Lesson.
- **A-6** (§4.2 FR-6): Teacher review shows full per-Block Citations; the Student Player shows a Lesson-level "Sources" section; per-Block Student display is roadmap (resolved, OQ-10).
- **A-7** (§4.2 FR-7): generation idempotency is keyed on a normalised request; exact normalisation is an architecture decision.
- **A-8** (§4.2 FR-8): job status states are at minimum queued / in progress / complete / failed; step-level progress desirable, not committed.
- **A-9** (§4.4 FR-14): narration content remains available as on-screen text when speech synthesis is unavailable.
- **A-10** (§4.4 FR-15): short-answer scoring is deterministic normalised matching (case/whitespace/punctuation) against Teacher-approved accepted-answer lists, editable in review; no LLM judging (resolved, OQ-4).
- **A-11** (§4.4 FR-17): a Simulation failing automated checks blocks publish with a Teacher-readable reason; the Teacher may delete the Block to proceed.
- **A-12** (§4.6 FR-22): the Player embeds in the Moodle page itself; pop-out playback is not required.
- **A-13** (§4.6 FR-23): gradebook/completion writeback failures are retriable without Student rework; mechanism is an architecture decision.
- **A-14** (§4.7 FR-26): feature-flag granularity includes at least the Diagram feature and Simulation Blocks, and toggling takes effect without redeploying (a strengthening beyond the brief's bare "feature flags").
- **A-15** (§7 Privacy): the platform stores minimum Student identifiers for attribution and no additional Student PII (resolved, OQ-8 — see NFR-9).
- **A-16** (§10 SM-C1): SM-C1 measures time-to-publish (calendar delay) from existing Structured Events; it is an honest proxy, not a review-effort measure — true review-effort instrumentation would be a scope addition.
- **A-17** (§10): the counter-metric set (SM-C1–SM-C3) is a PM addition beyond brief §4 — confirm or strike.
- **A-18** (§2.2): the Non-Users list is inferred from deployment context; not stated in the brief.
- **A-19** (§4.2 FR-4): Teacher identity and Course Context arrive via the signed, short-lived Launch Token from mod_edonlesson; no standalone login in MVP (resolved, OQ-11; FR-29).
- **A-20** (§4.3): creator-owns model — Drafts private to their creator; Published Versions Tenant-wide visible and duplicable; edit/republish restricted to owner + Tenant Admin; no co-editing (resolved, OQ-13; supersedes the earlier shared-authoring default).
- **A-21** (§11): MVP lesson quizzes are formative-stakes; answer exposure on the client is accepted; score forgery is closed by server-authoritative re-scoring (resolved, OQ-14; FR-15).
- **A-22** (§4.6 FR-23): completion = all Blocks viewed + all Quiz Blocks submitted; retakes with Teacher-configurable attempt limits; gradebook records the highest attempt; completions/grades pinned to the version taken, new attempts use the latest Published Version; resume is an architecture decision (resolved, OQ-15).
- **A-23** (§10 SM-2): per-Lesson denominator over a rolling 30-day window, with jobs-per-publish tracked as a churn guard.
- **A-24** (§10 SM-4): fully-loaded cost includes failed jobs and Regenerations, divided by Published Versions (resolved, OQ-1; $2 soft-alert threshold as tunable config).
- **A-25** (§10 SM-3): 24-hour eventual-consistency window for writeback.
- **A-26** (§4.1 FR-2): minor/major schema version-mismatch semantics — ratified during schema design in architecture.
- **A-27** (§4.3 FR-9): preview exposes poster/fallback states — a clarification of faithful preview, not new scope.
- **A-28** (§4.3 FR-10): per-Block-type editability map — text-bearing Blocks and Model3D annotations editable; Diagram SVG and Simulation code not editable in MVP, covered instead by committed Block-level Regeneration (OQ-3); Draft discard required (implied by the brief's draft lifecycle).
- **A-29** (§3, §4.7 FR-26): Budget Ceiling period is the calendar month; in-flight jobs run to completion; failed-job spend counts (resolved, OQ-9).
- **A-30** (§4.5 FR-21, §4.7 FR-26): cache hits do not consume Rate Limits; per-user Rate Limits ship as platform defaults overridable per Tenant; diagram Quota default 20/Student/day (resolved, OQ-2).
- **A-31** (§4.2 FR-6): Citations are per-Block — provenance always stored as a data-model requirement, preserved through edits as provenance-of-generation; deleted Blocks drop theirs (resolved, OQ-10).
- **A-32** (§10 SM-C1–C3): counter-metric triggers are provisional values, approved (resolved with OQ-1/OQ-2).
- **A-33** (§4.7 FR-27): the canonical event list extends the brief's six events with the failure/rejection events this PRD's own FRs and metrics require.
- **A-34** (§10 SM-1): the clock includes queue time; provisional p90 target of 2× the median bar; concurrency envelope set with the OQ-1 config values (resolved, OQ-1).
- **A-35** (§4.4 FR-17): minimum intent of the Simulation automated checks — loads without error, honors the postMessage protocol, exposes authored parameters, respects resource budgets.
