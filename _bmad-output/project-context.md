# Project Context — edon-lesson

> **Status:** Stakeholder seed. The Architect agent extends this at the end of Architecture Creation (adding decisions from the ADRs) but must not weaken or remove any rule marked **[HARD]**. Where this file conflicts with an agent's general habits, this file wins.

## 1. What This Project Is

e-DON Lesson Studio: a multi-tenant, curriculum-grounded AI lesson generation and delivery platform for ~60 Nigerian Colleges of Education, integrating with an existing Moodle LMS and an existing RAG backend (edon-rag) via API only. MVP scope and roadmap are defined in the Product Brief; this file governs *how* we build, not *what*.

Two economic/quality invariants shape every implementation decision:
- **[HARD] Generate-once:** lessons are generated on teacher request, cached, and replayed at near-zero marginal cost. Never introduce per-student-per-session LLM inference except where the brief explicitly allows it (on-demand diagrams).
- **[HARD] Review gate:** no AI-generated content reaches students unpublished, except sanitised on-demand SVG diagrams.

## 2. Technology Stack and Standards

- **Backend:** Python 3.12. Web framework per ADR-001 (Flask is the team standard; FastAPI is acceptable given async pipeline workloads and edon-rag precedent — the ADR must decide and all services follow it uniformly).
- **Frontend/player/authoring UI:** JavaScript with JSX. **[HARD] No TypeScript.** React for UI; the student player must also build as a self-contained embeddable bundle (script + mount API) that runs inside Moodle pages without a Next.js host.
- **3D:** Three.js rendering glTF assets. Assets are Draco-compressed with per-block size budgets and a poster-image fallback.
- **Data:** PostgreSQL for relational data; object storage for lesson assets with tenant-scoped path prefixes. Migrations are versioned and reversible.
- **Deployment:** Linux VPS, nginx reverse proxy, systemd services, Let's Encrypt TLS — matching existing team operational practice. Design generation workers so they can scale horizontally later; do not require it now.
- **Tooling:** Node 20+ for frontend builds. Python dependencies pinned; `pip` with a lockfile or `uv`.

## 3. LLM and Inference Policy

- **[HARD] All model access goes through a single provider-agnostic adapter** exposing an OpenAI-compatible chat-completions interface. No service calls a vendor SDK directly; no model identifier, endpoint, or API version is hardcoded anywhere outside configuration.
- **Per-workload model configuration.** Config defines a model (provider, model ID, endpoint, parameters) per workload key: `lesson_generation`, `simulation_generation`, `diagram_generation`, `embeddings`. Workloads may point at different providers simultaneously.
- **Launch configuration (subject to ADR-002 benchmark):**
  - `lesson_generation`, `simulation_generation`: current frontier API model (benchmark the leading tier on the actual pipeline; do not default to GPT-4o out of habit).
  - `diagram_generation`: mini/small-tier API model with structured-output support.
  - `embeddings`: existing Ollama `nomic-embed-text` via edon-rag (unchanged; retrieval is edon-rag's concern).
- **[HARD] Cost telemetry on every LLM call:** tokens in/out, computed cost, tenant, user, workload key, cache hit/miss, latency — persisted as structured events. This telemetry is the instrument for all future model-migration decisions.
- **Caching:** diagram requests are cached tenant-scoped on a normalised request key before any LLM call. Lesson generation results are persisted; regeneration is always an explicit user action.
- **Planned migration path (design for, do not build now):** when sustained monthly `diagram_generation` API spend exceeds ~60–70% of the cost of a rented 24 GB GPU instance for two consecutive months, evaluate migrating that workload to a self-hosted open-weight model (Qwen3-32B-class, INT4, served via vLLM with constrained/guided decoding for schema-valid output) behind the same adapter. Because the adapter is OpenAI-compatible, this migration must be achievable as a configuration change plus an evaluation pass — if it would require code changes in consuming services, the adapter is wrong.
- **Self-hosting constraint:** the existing CPU-only VPS must never be configured as a generation-model host. Self-hosted generation implies a GPU instance provisioned for that purpose.
- **Long-term direction (context for design decisions):** the V3 roadmap (streaming multi-agent classrooms) carries per-session inference economics; open-weight self-hosting on owned GPUs is the intended cost-control strategy at that stage. Prefer designs that keep prompts, tool contracts, and output schemas portable across providers.

## 4. Security Rules

- **[HARD] SVG sanitisation:** every LLM-generated SVG (teacher- or student-side) passes an allowlist-based sanitiser (strip scripts, event handlers, `foreignObject`, external references) before storage or rendering. Sanitisation failures reject the output; they never pass through raw.
- **[HARD] Simulation sandboxing:** simulation blocks execute only inside sandboxed iframes with a strict CSP: no network access, no parent-frame access beyond a defined postMessage protocol, no storage APIs.
- **[HARD] Tenant isolation everywhere:** every query, cache key, asset path, log line, and quota is tenant-scoped. Cross-tenant access paths must not exist, including in admin tooling, except through explicit operator-role endpoints.
- **[HARD] No wildcard CORS.** Allowed origins are per-tenant configuration.
- Secrets via environment configuration only; a maintained `.env.example` is committed; real secrets never are. API keys support rotation from day one (issue/revoke without downtime).
- Per-tenant budgets and per-user rate limits are enforceable at the adapter layer, not only at UI level.
- All logs include tenant and user identifiers (structured logging; no bare print statements).

## 5. Legal and Licensing Rules

- **[HARD] Clean-room constraint:** This product is behaviourally inspired by published research on multi-agent AI classrooms (Tsinghua MAIC). No code may be copied, ported, or adapted from the OpenMAIC repository (AGPL-3.0) or any other copyleft codebase. All implementation is original. Dev agents must not fetch, quote, or reference OpenMAIC source.
- Dependencies must carry permissive licenses (MIT/BSD/Apache-2.0 or compatible). No GPL/AGPL runtime dependencies in the platform. Exception: the companion Moodle plugin repo (`mod_edonlesson`) is GPLv3 as Moodle requires and stays thin — no proprietary logic lives in it.
- Every curated 3D asset stores its licence and attribution metadata; only openly licensed assets enter the library.

## 6. Architecture Principles

- **Schema-first:** the versioned Lesson Script Schema is a first-class package with validators, consumed by backend and player alike. Schema changes require a version bump and a documented migration/compatibility note. Players ignore unknown block types gracefully. Published lessons remain playable forever.
- **Extension points over speculation:** implement only MVP scope, but preserve the six V3-readiness seams from the brief (new block types via player block registry; delivery abstraction that is interface-compatible with streaming; narration provider interface; generic quota/budget subsystem; static self-containable published assets; LMS-agnostic platform API with Moodle specifics confined to the plugin). Do not build V3 features; do not paint over these seams either.
- **Async generation:** generation runs as queued jobs with progress reporting; the API never blocks a request on a full generation.
- **Immutable publications:** publishing produces an immutable version; edits create new drafts; republishing creates new versions.

## 7. Quality and Testing Expectations

- Unit tests for schema validation, sanitisation, quota/budget enforcement, and cost-telemetry emission are mandatory (these protect the [HARD] rules).
- The generation pipeline has golden-path integration tests using recorded/mocked LLM responses; prompts and pipeline steps are configuration/data, not inline constants, so they can be tuned without code releases.
- Player: cross-browser smoke tests plus a low-spec profile (throttled CPU, constrained memory) in CI for the block types with heavy assets.
- Every story's definition of done includes: logs structured, tenant-scoped, telemetry emitted, `.env.example` updated if config changed.

## 8. Repository Conventions

- Primary repo `edon-lesson`: `/schema` (lesson script schema package), `/backend` (services), `/player` (embeddable student player), `/authoring` (teacher UI), `/docs` (ADRs, runbooks). Companion repo `mod_edonlesson` (Moodle plugin, GPLv3).
- ADRs live in `/docs/adr` and are numbered; ADR-001 backend framework, ADR-002 launch model selection benchmark are reserved.
- Conventional commits; feature branches; no direct pushes to main once CI exists.
- External integration contracts (edon-rag retrieval API, Moodle plugin API) are documented in `/docs/integrations` and treated as versioned interfaces — changes to what we *need* from them become explicit work items, never assumed edits to external systems.

## 9. Architecture Decisions (extension, 2026-07-17)

> Appended by the Architect at the end of Architecture Creation, per the status line above. Additive only; no rule above is weakened. **Pending stakeholder sign-off of the architecture run 2026-07-17** — treat as binding once signed off. Rationale lives in `/docs/adr` and the architecture spine (`_bmad-output/planning-artifacts/architecture/architecture-2027_edon_sim_pro-2026-07-17/ARCHITECTURE-SPINE.md`), which downstream workflows consume alongside this file.

**ADR index (decisions of record):**
- **ADR-001 — FastAPI** (0.139.x, uvicorn, Pydantic v2) for the single backend deployable + workers; Flask remains the team default outside this repo.
- **ADR-002 — Model selection is a standing benchmark**, run through the production adapter with zero code changes per candidate; winners are dated ADR-002 addenda and land in per-workload config only. Current open-weight migration exemplar: Qwen3.6-35B-A3B (Apache-2.0, INT4 on 24 GB, vLLM guided decoding) — supersedes "Qwen3-32B-class" as the class example in §3's migration note (same intent, current model).
- **ADR-003 — Procrastinate 3.x on the platform PostgreSQL** (no Redis/RabbitMQ). Rule: any job whose loss violates a requirement is enqueued in the same transaction as the domain write it serves.
- **ADR-004 — Storage/versioning:** Lesson Scripts as validated JSONB; `published_versions` immutable at the database (no UPDATE/DELETE grants); one mutable Draft per Lesson with optimistic `revision`.
- **ADR-005 — Pipeline as config:** stages/prompts/retrieval params in versioned `pipeline.yaml` + prompt files; ungrounded generation fails (never an uncited Draft); per-Block `job_progress` events power authoring progress.
- **ADR-006 — Player:** self-contained IIFE (`EdonPlayer.mount`), ES2017/`chrome61` floor, React 19.2, all size/perf budgets in one CI-enforced `budgets.json` (core ≤ 150 kB gzip; heavy renderers and Showcase polish are lazy chunks).
- **ADR-007 — Simulation:** `sandbox="allow-scripts"` + CSP `default-src 'none'` + versioned postMessage protocol; dual mode `template|freecode` in the schema; headless pre-publish checks (incl. keyboard operability) gate publish.
- **ADR-008 — Tenant isolation mechanics:** `TenantContext` required for all data access + PostgreSQL RLS on every tenant-owned table (migration CI gate); operator access only via the audited operator router.
- **ADR-009 — Credentials (exactly five kinds):** tenant API keys (dual-valid, hashed), Launch Tokens (HS256, 120 s, single-use), Authoring Sessions (8 h), Playback tokens (24 h), Operator keys (CLI-issued, `/operator/*` only, audited). All lifetimes are config.
- **ADR-010 — Attempts:** an attempt = one Lesson run pinned to one Published Version, consumed at first quiz submission; scores stored as fractions (cross-version "highest attempt" = max fraction); submissions idempotent by client UUID, persisted + outboxed in one transaction before ack; grades/completions delivered via **pull-and-ack outbox** drained by the Moodle plugin's scheduled task.
- **ADR-011 — Data protection:** the LLM adapter's request types carry no identity fields; telemetry uses per-tenant HMAC pseudonyms; retention via `retention.yaml` (default 12 months); processor record in `/docs/processors.md`.
- **ADR-012 — Object storage:** `StorageDriver` port; launch driver = VPS filesystem + nginx `X-Accel-Redirect`; S3-compatible driver is the swap; MinIO excluded (AGPL). Publishing freezes assets into the immutable version prefix with a manifest.
- **ADR-013 — Governance:** quotas/rate limits/budgets are policies over one `action_type` vocabulary, enforced reserve→settle in the adapter call path; cache hits never charge; OQ-9 exhaustion semantics verbatim; default per-tenant generation concurrency 1 (keeps the budget overrun bound at one job, A-29).
- **ADR-014 — Player composition interfaces:** `BlockRegistry`, `LessonDeliverySource`, `NarrationProvider`, `ResultsSink` — each with exactly one MVP implementation, exercised on every play; these interfaces are the V3 seams (a)(b)(c)(e) in code form.

**Build rules added (bind all stories):**
- `core` imports no framework, queue, or vendor SDK; routers/tasks stay thin (import-linter CI contract).
- **No-TypeScript is CI-enforced:** a lint gate fails any `.ts`/`.tsx` file in `/player`, `/authoring`, `/schema/js` (makes §2's [HARD] rule mechanical). Python dependencies are managed with `uv` (lockfile committed), resolving §2's "pip with a lockfile or uv" either/or.
- **Licence-audit CI gate:** both lockfiles are checked against the §5 allowlist (MIT/BSD/Apache-2.0/PSF/OFL or compatible); a non-allowlisted direct or transitive dependency fails CI. (@gltf-transform 4.4.x verified MIT at the pinned version; the gate re-verifies on every upgrade — ADR-012.)
- **One test/lint toolchain:** pytest + ruff (backend), Vitest + ESLint + Prettier (JS), Playwright (E2E + CI low-spec profile) — per-story tool choices are not open.
- Every new tenant-owned table ships its RLS policy in the same Alembic migration — CI fails otherwise.
- The FR-27 event taxonomy is closed: PRD list + `diagram_review_completed`, `diagram_invalidated`, `operator_action`, `cost_alert`, `writeback_overdue`. New event types require an architecture/PRD note.
- The SVG sanitiser allowlist preserves `<title>`, `<desc>`, `role="img"`, `aria-label`, `aria-labelledby`; Lesson Script Schema v1.0 carries `altText`/`longDescription` for Diagram Blocks and Model3D/Simulation posters.
- Policy numbers (quotas, budgets, lifetimes, size budgets) are config, never code constants; `budgets.json` is the single budget source consumed by CI and validators.
- Platform API stays LMS-agnostic (Moodle knowledge only in `mod_edonlesson`); integration contracts live in `/docs/integrations` and change only via work items.
