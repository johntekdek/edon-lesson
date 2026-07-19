# PRD Addendum — e-DON Lesson Studio

Depth preserved from the Product Brief — material that belongs in downstream documents (architecture, UX, sprint planning), not in the PRD itself. `_bmad-output/project-context.md` is **authoritative** for build rules ([HARD] constraints); nothing here weakens it.

## 1. For the Architect

**ADR agenda (minimum, per brief §9/§12.3):**
- ADR-001 — backend framework: Flask (team standard) vs. FastAPI (async pipeline workloads; edon-rag precedent). Either acceptable; silence is not. All services follow the decision uniformly.
- ADR-002 — launch model selection benchmark: benchmark the leading frontier tier on the actual pipeline; do not default to GPT-4o out of habit. Per-workload keys: `lesson_generation`, `simulation_generation`, `diagram_generation`, `embeddings`.
- Lesson storage/versioning model (immutable Published Versions, coexisting Drafts).
- Generation pipeline design: queueing, caching, cost telemetry, prompts/pipeline steps as tunable configuration; stage shape per brief §5.2 (lesson plan → per-Block content → validation).
- Player embedding strategy for Moodle (self-contained bundle + mount API; no Next.js host requirement).
- Simulation sandboxing (iframe, strict CSP, postMessage protocol) and the automated pre-publish checks.
- Authoring launch security: the signed, short-lived Launch Token minted by mod_edonlesson (PRD FR-29) — token format, signing, lifetime, and replay protection.
- Data-protection mechanics (PRD NFR-9): identity-stripping of LLM-bound requests, telemetry pseudonymisation that preserves [HARD] attribution, configurable log retention (default 12 months).
- The six V3-readiness seams (below) demonstrated as extensions, not rewrites.
- At the end of architecture, extend `project-context.md` with ADR decisions — never weakening [HARD] rules (brief §12.3; project-context status line).

**V3-readiness seams (brief §10 — design for, do not build):**
(a) new Block types including agent-dialogue turns — schema versioning + player block-registry; (b) streaming lesson delivery — delivery abstraction interface-compatible with incremental blocks; (c) alternative narration providers — narration provider interface in the Player; (d) student-triggered generation with budget governance — quota/budget subsystem generic over generation types; (e) offline/SCORM export — published-lesson assets static and self-containable; (f) LTI 1.3 — Moodle specifics confined to the plugin, platform API LMS-agnostic.

**External integration contracts (brief §8 — greenfield boundary):**
- edon-rag: FastAPI, PostgreSQL + pgvector, Ollama `nomic-embed-text`, per-tenant API keys. Architect specifies the exact retrieval contract (query → ranked chunks with metadata/citations); gaps become integration work items, never edon-rag rewrites.
- Moodle 5.x: separate hosting, Almondb-based theme; grade/completion/web-service APIs only.
- LLM provider: OpenAI-compatible provider-agnostic adapter; per-workload model config; no hardcoded model strings (known defect elsewhere in the stack — do not repeat).
- 3D asset sources: Smithsonian 3D, NIH 3D, CC-licensed collections; licence metadata per asset.

**Cost-economics rationale (principle: brief §1/§11; specifics: project-context §3):**
Generate-once is the load-bearing economic principle; per-interaction spend is confined to diagram generation (mini/small-tier model with structured output). The migration trigger and target self-hosted stack are specified in `project-context.md` §3 (authoritative — numbers deliberately not restated here). Design consequence to preserve: migration must be achievable as a configuration change plus an evaluation pass — if it would require code changes in consuming services, the adapter is wrong. CPU-only VPS is never a generation host.

**Diagram generation note (brief §5.16):** the LLM may emit an intermediate text representation (e.g., Mermaid) rendered to SVG; every SVG so derived still passes Sanitisation (PRD FR-20) — the intermediate step grants no exemption.

**Simulation dual-mode note (brief §11):** design so that free-coded Simulations and a parameterised template library coexist; if free-code quality is poor at MVP, the template library is the fallback ship vehicle (PRD OQ-5).

## 2. For Sprint Planning / SM

**Story sequencing guidance (brief §12.5):** schema package first → generation-pipeline walking skeleton (topic → retrieval → one slide+quiz lesson → stored draft) → Player rendering that skeleton → review/publish → remaining Block types in order of increasing risk (Diagram → Model3D → Simulation) → Moodle module + gradebook writeback → student diagram generation. Hardening (quotas, budgets, logging) threaded throughout, never deferred to the end.

**Repository plan (brief §12.4):** primary greenfield repo `edon-lesson` (schema package, backend service(s), player, authoring UI — layout per project-context §8); companion repo `mod_edonlesson` (GPLv3, thin), plannable as a late epic once the platform API stabilises — now also home of the teacher-facing Authoring launch entry point (PRD FR-29). Third work item (PRD OQ-12, resolved): block_edon_ai enhancement, minimal surface — call the platform diagram endpoint and render the already-sanitised SVG it returns; Sanitisation, caching, Quotas, and identity-stripping stay server-side.

## 3. For UX

- Authoring UX must assume no prompt-engineering skill and moderate digital literacy overall (brief §3.1) — this bounds the whole authoring surface, not just prompting: Moodle-initiated entry with no login screen (PRD FR-29; course context arrives with the Launch Token); topic + optional guidance as plain fields; progress feedback during async generation; review surface with block-level edit (text, delete, reorder) plus regeneration for diagram/model3d/simulation blocks, citation visibility, faithful preview, explicit publish.
- Reported-diagram review queue for Teachers (PRD FR-28), and the "AI-generated — verify against your course materials" label on every diagram.
- Student Player: low-spec Android as a first-class design target; poster-fallback states are designed states, not error states.
- Diagram chat experience rides the existing block_edon_ai chat surface; quota/rate-limit messaging needs humane copy (PRD SM-C3 watches denial rates).

## 4. Deliberately Not in the PRD

- Tech stack, deployment, testing standards, repo conventions: `project-context.md` §§2, 7–8 (authoritative). Architecture principles (§6) are reflected in the PRD at capability level only; their build-rule form remains authoritative in project-context.
- Clean-room/licensing rules: `project-context.md` §5 [HARD]; restated in PRD NFR-7 only at capability level.
- Model/provider specifics and migration path: `project-context.md` §3 + §1 of this addendum.
