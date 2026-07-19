# Product Brief — e-DON Lesson Studio

**Artifact type:** BMAD Method Phase 1 output (Product Brief), authored by product stakeholder; hand to PM agent as input to the PRD workflow.
**Project codename:** `edon-lesson`
**Date:** 6 July 2026
**Suggested BMAD planning level:** Level 3 (new multi-service product with external integrations)

---

## 1. Executive Summary

e-DON Lesson Studio is a curriculum-grounded AI lesson generation and delivery platform, built as the next evolution of the deployed e-DON SIM PRO product (a Moodle-based LMS with RAG-powered AI assistance serving ~60 Nigerian Colleges of Education). Teachers generate interactive lessons — slides, narration, quizzes, accurate technical diagrams, interactive 3D models, and parameter-manipulable simulations — from their institution's own curriculum corpus, review and approve them, and publish them into Moodle courses where students consume them with grades flowing to the Moodle gradebook. Students can additionally generate accurate labelled diagrams on demand.

**Build posture:** MVP scope (defined below) on a V3-ready architecture. The long-term vision is a fully immersive multi-agent AI classroom (streaming AI teacher, AI classmates, live Q&A, adaptive sequencing). Nothing in that vision is built now, but every architectural decision must make it an *addition*, never a rewrite.

**Core economic principle (load-bearing, non-negotiable):** lessons are generated once, cached forever, and replayed at near-zero marginal cost. Per-interaction LLM spend is confined to the one deliberately cheap student-facing feature (diagram generation). Any design that introduces per-student-per-session inference into the MVP violates this brief.

**Core quality principle (load-bearing, non-negotiable):** no AI-generated content reaches students without passing a teacher review-and-publish gate, except sanitised on-demand SVG diagrams.

## 2. Problem Statement

Nigerian Colleges of Education using e-DON SIM PRO have strong LMS infrastructure (courses, enrolment, assessment, gradebook) and a working RAG chat assistant grounded in institutional documents, but course content itself remains static: PDFs, text pages, and conventional quizzes. Producing interactive, visual, curriculum-aligned learning material is beyond the time budget and tooling of most lecturers. Existing AI education products generate generic content ungrounded in the institution's actual syllabus, carry per-interaction costs unsuited to large student populations, and do not integrate with institutional gradebooks. The gap: a way for teachers to turn their existing curriculum corpus into reviewed, interactive, gradebook-connected lessons in minutes rather than weeks.

## 3. Users

1. **Lecturers / teacher-trainers (primary authors).** Subject experts, moderate digital literacy, time-poor. They initiate generation, review and edit lesson content, approve publication, and monitor results. The authoring UX must assume no prompt-engineering skill.
2. **Pre-service teacher students (primary consumers).** Access lessons inside Moodle courses on a wide range of devices, including low-spec Android hardware. They complete lessons, take embedded quizzes, manipulate simulations and 3D models, and request diagrams via the existing AI chat.
3. **College administrators / sponsors (secondary).** Need evidence of usage and outcomes. MVP provides event logging sufficient to build reporting later; no dashboard in MVP.
4. **Platform operator (internal).** Manages tenants, API keys, quotas, and cost controls across ~60 institutions from a single multi-tenant deployment.

## 4. Goals and Success Metrics

**Product goals:** (a) lecturers produce and publish grounded interactive lessons without technical help; (b) students complete lessons with quiz scores captured in the Moodle gradebook; (c) unit economics hold at scale.

**MVP success metrics:**
- Median time from "teacher initiates generation" to "lesson ready for review" under 5 minutes.
- ≥ 70% of generated lessons reach published state (proxy for generation quality; if teachers discard most drafts, generation is failing).
- Lesson completion and quiz score writeback functioning for 100% of published lessons.
- Fully-loaded generation cost per lesson below a defined ceiling (PM to set with stakeholder; target order-of-magnitude: single-digit USD), and near-zero marginal cost per student replay.
- On-demand diagram requests served under a defined per-request cost with cache hit rate tracked.

## 5. MVP Scope — Functional Requirements

### FR-A. Lesson generation (teacher-initiated)
1. Teacher supplies topic, course context, and optional guidance; the system retrieves relevant grounding chunks from the institution's corpus **via the existing edon-rag retrieval API** (external system — see §8), scoped to the teacher's tenant.
2. A generation pipeline orchestrates LLM calls to produce a lesson conforming to the versioned Lesson Script Schema (§6): lesson plan → per-block content → validation.
3. Every generated lesson stores source citations linking content back to retrieved corpus chunks.
4. Generated lessons are persisted as drafts. Generation is idempotent and cached: regeneration is an explicit teacher action, never implicit.
5. Generation requests are queued and processed asynchronously with progress feedback to the teacher.

### FR-B. Review and publish workflow
6. Teachers can preview the full lesson exactly as students will see it.
7. Teachers can edit lesson content at block level (text edits at minimum; block deletion and reordering required; block-level regeneration desirable).
8. Publication is an explicit teacher action producing an immutable published version; drafts and published versions coexist; republishing creates a new version.
9. Nothing is student-visible until published. No exceptions in MVP other than FR-D diagrams.

### FR-C. Lesson player (student-facing)
10. A JavaScript player renders published lessons: slide sequence, narration, embedded quizzes, diagrams, 3D model blocks, simulation blocks.
11. Narration in MVP uses the browser SpeechSynthesis API (no server-side TTS). The player must treat narration audio as a swappable provider (V3-readiness: pre-generated neural TTS, then streaming TTS, plug in later).
12. Quiz blocks support at minimum multiple-choice and short-answer with defined answers/feedback; scoring happens client-side against the published script, with results reported to the backend and to Moodle (FR-E).
13. 3D model blocks render curated glTF assets in a Three.js viewer with orbit/zoom and authored annotations. Models come from a curated, curriculum-mapped internal library (MVP seeds this library manually; AI *selects and configures* models during generation — it never generates 3D geometry).
14. Simulation blocks run in sandboxed iframes (no network access, strict CSP) and expose authored manipulable parameters (sliders/inputs) to students. Simulation code is produced during teacher generation and is subject to the review gate plus automated checks before publish.
15. The player must perform acceptably on low-spec Android devices; heavy assets (glTF) require compression (e.g. Draco) and size budgets.

### FR-D. Student on-demand diagram generation
16. Students can request accurate labelled technical diagrams (SVG, LLM-generated; Mermaid acceptable as an intermediate representation) from within the existing AI chat experience, grounded in the tenant corpus.
17. All generated SVG passes a mandatory sanitisation pass (script/foreignObject/event-handler stripping, allowlist-based) before rendering. This applies to teacher-side diagrams too.
18. Diagram requests are cached (tenant-scoped, keyed on normalised request) and rate-limited per student with per-tenant quotas.

### FR-E. Moodle integration
19. A Moodle activity module (`mod_edonlesson`, separate companion repository, GPLv3 as Moodle requires — keep it thin; all proprietary logic stays server-side) lets teachers place a published lesson into a course, and embeds the player for students.
20. The module reports completion to Moodle completion tracking and writes quiz scores to the Moodle gradebook via Moodle's grade APIs.
21. Authentication between the module and the platform uses tenant-scoped credentials consistent with the existing block_edon_ai / edon-rag pattern; student identity is passed so results attribute correctly.

### FR-F. Multi-tenancy, administration, and cost control
22. Full tenant isolation for lessons, assets, caches, quotas, and logs, consistent with the existing edon-rag multi-tenant model (~60 tenants at launch).
23. Per-tenant configuration: LLM budget ceilings, generation quotas, diagram quotas, feature flags.
24. Structured event logging (lesson generated / published / started / completed, quiz submitted, diagram requested) sufficient to power a future analytics dashboard. Include user and tenant identifiers in all logs (a known gap in the existing edon-rag query logs — do not repeat it).

## 6. The Lesson Script Schema (keystone artifact)

A versioned JSON schema (`"schema": "1.0"`) is the contract between generator, player, and all future renderers. It defines: lesson metadata (tenant, course reference, curriculum reference, version, citations), an ordered block list, and block types `slide`, `narration`, `quiz`, `diagram`, `model3d`, `simulation`. Design rules:

- **Forward-compatible by construction:** players must ignore unknown block types gracefully; schema versioning is explicit; published lessons must remain playable forever.
- **Reserved for V3 (do not implement, do not preclude):** dialogue/agent-turn block types, adaptive branching metadata, streaming delivery of blocks.
- The schema, its validators, and its documentation live in the new repository as a first-class package consumed by both backend and player.

## 7. Explicitly Out of Scope for MVP (roadmap, not backlog)

The PM agent must not promote these into MVP requirements: server-side/neural TTS; multi-agent classroom features of any kind (AI teacher persona, AI classmates, live Q&A, adaptive sequencing); student-triggered simulation generation; cross-tenant lesson sharing/library; analytics dashboard UI; offline/SCORM export (designed-for but not built — the schema and static-asset discipline must keep it cheap to add as a fast-follow); LTI 1.3 support for non-Moodle LMSs; AI illustrative image generation; text-to-3D generation.

## 8. External Systems and Integration Contracts (greenfield boundary)

This is a **greenfield build in a new repository**. The following existing systems are external dependencies accessed only via APIs — BMAD agents must not assume access to their source code and must design against these contracts:

1. **edon-rag** (existing production RAG backend: FastAPI, PostgreSQL + pgvector, Ollama `nomic-embed-text` embeddings, multi-tenant with per-tenant API keys, hosted on a VPS). Provides tenant-scoped retrieval. The Architect should specify the exact retrieval contract needed (query → ranked chunks with metadata/citations) and flag any gaps as integration work items, not as edon-rag rewrites.
2. **Moodle 5.x** (existing production LMS, separate hosting, Almondb-based theme). Integration exclusively through the companion `mod_edonlesson` plugin and Moodle's own APIs (grade, completion, web services).
3. **LLM provider** (currently OpenAI GPT-4o). All model access goes through a provider-agnostic adapter with configurable model identifiers — no hardcoded model strings (a known defect in the existing stack; do not repeat it).
4. **3D asset sources** for the curated library (openly licensed: e.g. Smithsonian 3D, NIH 3D, CC-licensed collections). Licence metadata must be stored per asset.

## 9. Technical Constraints and Team Standards

- **Backend:** Python 3.12. The team standard for new microservices is Flask; the adjacent edon-rag service is FastAPI. The Architect must choose one for this repo and record the decision as an ADR — async generation-pipeline workloads may justify FastAPI; consistency with team standards may justify Flask. Either is acceptable; silence is not.
- **Frontend/player:** JavaScript/JSX only — **no TypeScript** (team standard). The player must be embeddable as a self-contained bundle inside Moodle pages (not only inside a Next.js app). Three.js for 3D. Any authoring UI follows the same standard.
- **Data:** PostgreSQL. Object storage for lesson assets (glTF, media) with tenant-scoped paths.
- **Deployment:** Linux VPS, nginx, systemd, Let's Encrypt — matching existing operational practice. Design for a single-VPS start with a path to horizontal scaling of the generation workers.
- **Security requirements (hard):** SVG sanitisation allowlist (FR-D.17); simulation iframe sandboxing with strict CSP and no network; tenant isolation everywhere; no wildcard CORS (known defect elsewhere in the stack — do not repeat); secrets via environment configuration with a committed `.env.example`; API key rotation supported from day one.
- **Legal/clean-room constraint (hard):** This product is behaviourally inspired by published research on multi-agent AI classrooms (Tsinghua MAIC). **No code may be copied, ported, or adapted from the OpenMAIC repository (AGPL-3.0) or any other copyleft codebase.** All implementation is original. Dev agents must not fetch, quote, or reference OpenMAIC source. This constraint goes into `project-context.md` verbatim.

## 10. V3-Readiness Architectural Requirements (for the Architect agent)

The Architect must demonstrate, in the architecture document, how each of the following future capabilities lands as an *extension* rather than a rewrite: (a) new block types including agent-dialogue turns — via schema versioning and player block-registry design; (b) streaming lesson delivery — via a delivery abstraction that today returns a complete published script but is interface-compatible with incremental block delivery; (c) alternative narration providers (pre-generated neural TTS, then streaming TTS) — via a narration provider interface in the player; (d) student-triggered generation with budget governance — via the quota/budget subsystem being generic over generation types, not hardcoded to diagrams; (e) offline/SCORM export — via all published-lesson assets being static and self-containable; (f) LTI 1.3 — via keeping Moodle-specific logic confined to the plugin, with the platform API remaining LMS-agnostic.

## 11. Risks and Assumptions

- **Generation quality risk:** grounded lesson generation may need significant prompt/pipeline iteration before the 70% publish-rate target is met. Mitigation: the review gate absorbs quality variance; treat the pipeline as tunable configuration, not code constants.
- **Simulation safety/quality risk:** LLM-written simulation code is the highest-variance MVP feature. Mitigation: sandbox + automated checks + mandatory teacher preview; if quality is poor at MVP, ship with a small library of parameterised simulation templates the generator configures instead of free-coding — the Architect should design so both modes coexist.
- **Device performance risk:** 3D and simulations on low-spec hardware. Mitigation: asset budgets, compression, graceful degradation (poster image fallback per block).
- **Cost risk:** generation cost creep. Mitigation: per-tenant budgets (FR-F.23), cost telemetry per generation, caching discipline.
- **Assumptions:** edon-rag retrieval quality is sufficient as-is for grounding (validated by existing chat usage); adequate internet bandwidth at institutions for online delivery (offline export remains a designed-for fast-follow); English-language content at launch with localisation-ready text handling.

## 12. Handover Notes for the BMAD Run

1. **Phase 1 (Analysis) is complete** — this brief is its output. Do not re-run brainstorming; proceed to Phase 2 (Planning / PRD workflow) with this brief as input.
2. **PM agent:** derive the PRD strictly from §5–§7. Scope changes in either direction require explicit stakeholder confirmation — in particular, do not de-scope the review gate, the schema-first design, or tenant isolation, and do not pull §7 items into MVP.
3. **Architect agent:** produce the architecture plus ADRs for, at minimum: backend framework choice (§9), lesson storage/versioning model, generation pipeline design (queueing, caching, cost telemetry), player embedding strategy for Moodle, simulation sandboxing, and the §10 extension points. Generate `project-context.md` at the end of architecture, including the team standards and the clean-room constraint from §9 verbatim.
4. **Repository plan:** primary greenfield repo `edon-lesson` (schema package, backend service(s), player, authoring UI); companion repo `mod_edonlesson` (Moodle plugin, GPLv3, thin). The Moodle plugin can be planned as a late epic once the platform API stabilises.
5. **Story sequencing guidance for the SM agent:** schema package first; then generation pipeline walking skeleton (topic → retrieval → one slide+quiz lesson → stored draft); then player rendering that skeleton; then review/publish; then remaining block types (diagram → model3d → simulation, in that order of increasing risk); then Moodle module and gradebook writeback; then student diagram generation; hardening (quotas, budgets, logging) threaded throughout, not deferred to the end.
