# ADR-005: Generation Pipeline Design

**Status:** Accepted (stakeholder sign-off, 2026-07-18)

## Context
FR-4–FR-8: queued async generation, lesson plan → per-Block content → validation, citations, caching, explicit regeneration; prompts and pipeline steps are configuration, not code constants (project-context §7); per-Block progress events (UX amendment E); block-level Regeneration for Diagram/Model3D/Simulation (FR-10).

## Decision
**Pipes-and-filters** pipeline executed inside a Procrastinate job (ADR-003), defined as data:

- `pipeline.yaml` (versioned config, hot-reloadable per deploy): ordered stages with per-stage prompt template refs, workload key, retrieval parameters, repair-loop policy (one schema-repair retry per stage), and output validators. Prompt templates are files under `backend/config/prompts/`, language-keyed, with the stable-prefix ordering rule (system + Grounding Chunks first) for provider prefix caching.
- **Retrieval is course-scoped** (edon-rag contract v1.1): `POST /api/courses/{moodle_course_id}/retrieve`, `x-api-key`-authed; the course id comes from the Launch Token's `course_ref`. The live-retrieval slice is blocked on **WI-RAG-0** (no retrieval endpoint exists in production); recorded fixtures unblock pipeline development meanwhile.
- Stage shape (MVP): `plan` (retrieval → lesson outline + curriculum-ref derivation — **topic-derived** (`{value, source: pipeline}`, Teacher-correctable in review; chunk-tag derivation deferred with WI-RAG-2) + per-Block briefs) → `block_content` (fan-out per planned Block: slide/narration/quiz text; diagram via `diagram_generation` workload; model3d = **selection** from the Curated Model Library index + annotation authoring — never geometry; simulation via `simulation_generation` workload) → `assemble_validate` (script assembly, `/schema` validation, citation stitching, `altText` population, poster selection/production) → persist Draft.
- **Poster production is deterministic capture from the content itself** — Model3D: pre-rendered viewer captures made at library ingest; Simulation: headless screenshot at `sim:ready` (the ADR-007 check harness produces it); Diagram: the SVG renders directly. No image-generation model exists anywhere in the pipeline (PRD §8 fence).
- Every stage emits a `job_progress` row (`job_id, block_ref, stage, state, at`) — the source of the per-Block assembly showpiece; the Authoring UI consumes them via SSE with polling fallback. Absence of fine-grained rows degrades the card to coarse states (A-8 floor).
- **Grounding rule (A-5):** if `plan` retrieval yields no chunk above the score floor, the job fails `ungrounded` with the Teacher-readable reason; no uncited lesson is ever produced.
- **Block-level Regeneration** re-runs only that Block's stage with the same pipeline config and fresh retrieval for that Block's brief, revalidates (and re-runs FR-17 checks for Simulation), and replaces the Block in the Draft atomically.
- Cost accounting: every adapter call carries `(tenant, user pseudonym, workload, job_id, lesson_id)` so Cost Telemetry aggregates to per-Lesson fully-loaded cost (SM-4) without joins outside the telemetry store.
- Failure semantics: a stage failure after retries fails the whole job (FR-5 — no partial Draft); the job's real spend still settles against the Budget (A-29).

## Consequences
- **TTS is a publish-time stage, not a generation stage** (stakeholder amendment 2026-07-18): the publish job runs the `tts` workload per changed Narration Block (text-hash comparison), stores audio as static lesson assets in the frozen manifest, and republish regenerates only changed audio — per-lesson cost, zero per-student cost (I-1). See AD-5/ADR-004.
- Prompt/pipeline tuning is a config release, not a code release (SM-2 iteration risk absorbed).
- The fan-out per Block bounds wall-clock: per-Block stages run concurrently up to a per-job concurrency limit (config, default 4) — SM-1's 5-minute median is a pipeline-config concern, benchmarked in ADR-002.
- New Block types (V3 seam a) = new stage entry + schema minor bump + player registry entry; the pipeline engine is type-agnostic.
