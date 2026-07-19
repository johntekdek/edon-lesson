# Reconciliation Review — Architecture vs project-context.md (constitution)

**Run:** architecture-2027_edon_sim_pro-2026-07-17 · **Reviewed:** 2026-07-17
**Deliverable:** ARCHITECTURE-SPINE.md, docs/adr/ADR-001..013, docs/integrations/* (3 docs)
**Authority:** `_bmad-output/project-context.md` §§1–8 (pre-existing constitution); §9 checked as the run's own extension for non-weakening.

**Verdict:** The architecture satisfies every [HARD] rule in §§1–8 with a named mechanism except one enforcement gap (no-TypeScript, High), and §9 weakens nothing in §§1–8. One unflagged licensing violation in the stack table (Critical). All six V3 seams preserved; ADR reservation rule honored.

**Counts:** Critical 1 · High 1 · Medium 2 · Low 8

---

## CRITICAL

### C1 — §5 permissive-licence rule violated by `@gltf-transform/cli` 4.4.x (unflagged)
- **Constitution:** §5 "Dependencies must carry permissive licenses (MIT/BSD/Apache-2.0 or compatible)."
- **Architecture:** ARCHITECTURE-SPINE.md Stack table row `@gltf-transform/cli 4.4.x`; ADR-012 ingest pipeline step `gltf-transform optimize`.
- **Problem:** From glTF-Transform v4 the **CLI package** moved off MIT to a dual licence (Prosperity Public License 3.0 — noncommercial only — with paid commercial licences); only the SDK packages (`@gltf-transform/core`, `/extensions`, `/functions`) remained MIT. Running the v4 CLI in a commercial platform's operator ingest pipeline is a commercial use. The deliverable shows licence diligence elsewhere (MinIO excluded for AGPL, httpx maintenance flagged) but this one is not flagged anywhere — so it fails both the rule and the "deliberate, flagged deviation" escape hatch.
- **Fix (one line):** Replace the CLI with the MIT-licensed `@gltf-transform/functions`+`core` called programmatically in the ingest script (or pin the MIT v3 CLI, or purchase a commercial licence and record the deviation in ADR-012); verify exact v4.4 terms at fix time.

## HIGH

### H1 — §2 [HARD] "No TypeScript" has no landing rule or enforcement mechanism
- **Constitution:** §2 "**[HARD] No TypeScript.**"
- **Architecture:** Only a passing mention in ADR-007→ADR-006 *Context* ("no Next.js host, no TypeScript"). The spine's Consistency Conventions, §9 build rules, and CI gates (which exist for import-linter, RLS, budgets.json) never state or enforce it.
- **Risk:** Every other [HARD] rule got an explicit AD rule or CI contract; this one can silently drift in stories (e.g. a dev agent scaffolding Vite+TS).
- **Fix (one line):** Add "JavaScript + JSX only; no `.ts`/`.tsx` files (CI lint gate)" to the spine Consistency Conventions (Naming row or new row) and the §9 build-rules list.

## MEDIUM

### M1 — defusedxml is load-bearing for a [HARD] gate but absent from the Stack seed
- **Constitution:** §4 [HARD] SVG sanitisation (mechanism: AD-13 "defusedxml-parsed" allowlist sanitiser); §5 licence rule; §2 "Python dependencies pinned."
- **Architecture:** AD-13 names defusedxml; ARCHITECTURE-SPINE.md Stack table omits it (so it escapes the pin/licence sweep). Licence itself is fine (PSF-2.0). lxml is not used anywhere in the deliverable (n/a).
- **Fix:** Add a `defusedxml` row (PSF-2.0) to the Stack table.

### M2 — §7 low-spec CI profile omits the "constrained memory" dimension
- **Constitution:** §7 "a low-spec profile (throttled CPU, **constrained memory**) in CI."
- **Architecture:** AD-11 / ADR-006 profile = Playwright + CDP CPU 6× + 400 kbps/400 ms RTT only; memory constraint exists only for Simulation checks (heap ≤ 128 MB, ADR-007), not the Player profile.
- **Fix:** Add a memory dimension to the CI profile (e.g. `deviceMemory` spoof to tier-demote + a heap ceiling assertion on heavy Blocks) or record the omission as a flagged deviation with rationale.

## LOW

### L1 — Preact swap "recorded stakeholder option" vs §2 "React for UI"
- **Constitution:** §2 "React for UI" (non-HARD). **Architecture:** Stack React row; ADR-006.
- **Fix:** Fine as an option; note that exercising it requires a §2 amendment + ADR addendum (Preact is MIT — no §5 issue).

### L2 — §2 "object storage" launches as VPS filesystem
- **Constitution:** §2 "object storage for lesson assets with tenant-scoped path prefixes." **Architecture:** ADR-012 / AD-9 — filesystem behind `StorageDriver` port, tenant prefixes intact, S3-compatible swap documented.
- **Fix:** Deliberate and recorded — keep it explicitly in the sign-off batch as an interpretation note.

### L3 — §3 `embeddings` workload key not represented in the adapter
- **Constitution:** §3 per-workload config lists four keys incl. `embeddings`. **Architecture:** AD-3 lists three; ADR-002 marks embeddings "Not benchmarked. Fixed"; edon-rag doc §4 places it inside edon-rag (consistent with §3's own "unchanged; retrieval is edon-rag's concern").
- **Fix:** Add one clarifying line to AD-3 that `embeddings` is deliberately external (edon-rag/Ollama), not a platform adapter workload.

### L4 — [HARD] cost-telemetry field set never enumerated in the deliverable
- **Constitution:** §3 [HARD] telemetry = tokens in/out, computed cost, tenant, user, workload, cache hit/miss, latency. **Architecture:** AD-3/AD-8/AD-19 + `COST_TELEMETRY` entity mandate the call-path mechanism, but no document restates the seven fields the mandatory unit test (§7) must protect.
- **Fix:** Enumerate the field set in AD-19 or ADR-011 so the telemetry-emission unit test has a testable contract.

### L5 — §2 tooling choice (pip+lockfile vs uv) undecided
- **Constitution:** §2 "`pip` with a lockfile or `uv`." **Architecture:** Stack note "code owns exact pins once lockfiles exist" — tool never chosen.
- **Fix:** Add to the spine's Deferred table with a "first epic" revisit.

### L6 — anthropic-native driver's client dependency missing from Stack seed
- **Constitution:** §2 pinning + §5 licence sweep. **Architecture:** AD-3/ADR-002 define the `anthropic-native` translating driver; its HTTP client (anthropic SDK, MIT, or bare httpx) is unnamed.
- **Fix:** Name the driver's client library in the Stack table.

### L7 — Showcase fonts are SIL OFL 1.1, not MIT/BSD/Apache
- **Constitution:** §5 permissive rule. **Architecture:** ADR-006 showcase chunk embeds Inter + Plus Jakarta Sans subsets.
- **Fix:** OFL-1.1 is permissive-compatible for embedding — record it in the licence/attribution notes (same discipline as §5's 3D-asset rule).

### L8 — §6 "validators… consumed by backend and player alike" vs no runtime validation in Player
- **Constitution:** §6 schema-first. **Architecture:** AD-10 "No runtime schema validation in the Player (scripts arrive server-validated)"; player consumes the schema package via fixtures/toolchain (ajv, CI-only).
- **Fix:** Acceptable deliberate interpretation (bundle budget); already recorded in AD-10 and the Stack ajv row — no change required, keep the rationale.

---

## Rule-by-rule verification matrix (§§1–8)

### §1
| Rule | Status | Mechanism / landing |
| --- | --- | --- |
| [HARD] Generate-once | PASS | AD-5 (persisted immutable versions), AD-17 (queued jobs, explicit regeneration), AD-8/ADR-013 ("replay path contains zero governed calls"), diagram cache before LLM (ADR-013/ER `DIAGRAM_CACHE`); diagram carve-out honored |
| [HARD] Review gate | PASS | Students reach content only via playback sessions resolving Published Versions (ADR-010, integrations/mod-edonlesson §2.3, picker `published=1`); publish = validated transaction (AD-5); diagrams pass AD-13 sanitiser + FR-28 report/review queue |

### §2
| Rule | Status | Mechanism |
| --- | --- | --- |
| Python 3.12 | PASS | Stack [ADOPTED] |
| Framework per ADR-001, uniform | PASS | ADR-001 decides FastAPI, divergence from Flask team standard deliberately recorded; §9 consistent |
| JS + JSX, [HARD] no TypeScript | **GAP → H1** | Only ADR-006 Context mention; no rule/CI |
| React for UI | PASS (see L1) | React 19.2, Authoring + Player |
| Self-contained embeddable player bundle | PASS | AD-11/ADR-006 IIFE `EdonPlayer.mount`, no host framework |
| Three.js + glTF + Draco + budgets + poster fallback | PASS | AD-11 budgets.json, ADR-006/012 Draco ingest, posters, AD-12/AD-18 poster fallback |
| PostgreSQL; object storage w/ tenant prefixes; reversible migrations | PASS (see L2) | AD-5, AD-9/ADR-012 path law, Alembic reversible (Conventions row) |
| VPS/nginx/systemd/Let's Encrypt; workers horizontally scalable later | PASS | Deployment diagram (certbot.timer, systemd units); ADR-003 worker-host scale path |
| Node 20+; pinned Python deps | PASS (see L5) | Stack rows |

### §3
| Rule | Status | Mechanism |
| --- | --- | --- |
| [HARD] Single adapter, OpenAI-compatible, nothing hardcoded | PASS | AD-3; two internal drivers justified (ADR-002 fact 1 — Anthropic compat endpoint verified test-grade); [HARD] holds at consumer boundary; config-only per workload |
| Per-workload model config | PASS (see L3) | AD-3 + ADR-002 table; embeddings deliberately external |
| Launch config via benchmark, no GPT-4o habit | PASS | ADR-002 candidate matrix + selection rules; winners = dated addenda, config-only |
| [HARD] Cost telemetry every call | PASS (see L4) | AD-3 call path, AD-19 tables, ADR-005 accounting tuple, ADR-011 pseudonyms |
| Diagram cache before LLM; persisted lessons; explicit regen | PASS | ADR-013 cache-only semantics, AD-17, ADR-005 |
| Migration path = config change + eval pass | PASS | ADR-002 harness proves config-only swap; vLLM in openai-compatible driver; Qwen3.6-35B-A3B exemplar supersession explicitly flagged, same intent — no weakening |
| CPU-only VPS never a generation host | PASS | Spine Deployment section "[ADOPTED §3]" — GPU instance behind same adapter |
| Portable prompts/schemas | PASS | AD-17 config pipeline, sampling-param-free defaults (ADR-002 fact 2), stable-prefix ordering |

### §4 (one by one)
| Rule | Status | Mechanism |
| --- | --- | --- |
| [HARD] SVG sanitisation | PASS | AD-13 single server-side allowlist gate (defusedxml), reject-on-fail, both sides, no Mermaid exemption; DOMPurify defense-in-depth only; §9 aria-preservation strengthens, doesn't weaken |
| [HARD] Simulation sandboxing | PASS | AD-12/ADR-007: `sandbox="allow-scripts"` (never allow-same-origin → opaque origin kills storage APIs), CSP `default-src 'none'` (kills network), versioned postMessage only ('unsafe-inline' script/style grants no network/parent/storage — not a weakening) |
| [HARD] Tenant isolation everywhere | PASS | AD-6/ADR-008 dual layer: TenantContext-required repositories + RLS w/ migration CI gate; path/cache-key helpers; audited operator router = the sanctioned carve-out |
| [HARD] No wildcard CORS | PASS | ADR-008 ("no wildcard anywhere including error paths"), per-tenant origins from config; integrations/mod-edonlesson §1 |
| Secrets via env; .env.example; day-one rotation | PASS | Conventions config row, AD-18, ADR-009 dual-valid keys/secrets (all four kinds rotate without downtime) |
| Budgets/rate limits at adapter layer | PASS | AD-8/ADR-013 reserve→settle in adapter call path |
| Structured logs w/ tenant+user ids | PASS | AD-19 middleware-bound tenant_id + pseudonym (pseudonym = stable user identifier per NFR-9 — attribution preserved) |

### §5
| Rule | Status | Mechanism |
| --- | --- | --- |
| [HARD] Clean-room (no OpenMAIC/copyleft) | PASS | No OpenMAIC reference anywhere in deliverable; AGPL-awareness demonstrated (MinIO exclusion, ADR-012); constitution co-consumed by downstream stories |
| Permissive dependencies | **FAIL → C1** (one package) | See licence audit below |
| 3D asset licence/attribution metadata | PASS | ADR-012 ingest mandatory licence field + manifest licence records |

### §6
| Rule | Status | Mechanism |
| --- | --- | --- |
| Schema-first | PASS (see L8) | AD-2: versioned package, minor/major law, CI mirror-equivalence, migration notes; unknown blocks skipped (AD-10); playable forever (AD-5/AD-9 freeze) |
| Extension points / six V3 seams | PASS | Spine "V3 seams" table demonstrates all six — see seam check below |
| Async generation, non-blocking API | PASS | AD-4/AD-17/ADR-003 queued jobs + `job_progress` SSE; sync diagram endpoint (60 s) is the §1 diagram carve-out, not "full generation" |
| Immutable publications | PASS | AD-5/ADR-004: no UPDATE/DELETE grants; drafts→new versions |

### §7
| Rule | Status | Mechanism |
| --- | --- | --- |
| Mandatory unit tests (schema/sanitiser/governance/telemetry) | PASS | Conventions "Testing floors" row names all four as [HARD] protectors |
| Golden-path pipeline tests, recorded LLM fixtures; prompts as config | PASS | Testing floors + staging gate + AD-17/ADR-005 |
| Cross-browser smoke + low-spec profile | PARTIAL → M2 | AD-11 CI profile (CPU + network; memory missing) |
| DoD (logs/telemetry/.env.example) | PASS | Testing floors row defers to §7 verbatim; AD-18 |

### §8
| Rule | Status | Mechanism |
| --- | --- | --- |
| Repo layout | PASS | Source tree matches `/schema /backend /player /authoring /docs`; mod_edonlesson GPLv3 thin; block_edon_ai additive (OQ-12), no conflict |
| ADR numbering + reservations | PASS | ADR-001 = backend framework, ADR-002 = launch model benchmark, exactly as reserved; `ADR-NNN-slug.md` convention |
| Conventional commits / branches / no direct push | PASS | Conventions Git row [ADOPTED] |
| Integration contracts in /docs/integrations, versioned, changes = work items | PASS | Three v1 docs; WI-RAG-1..4 / WI-MOD-1..3 / WI-CHAT-1..3 discipline explicit; "never assumed edits to external systems" restated |

---

## §9 non-weakening check

Each §9 line checked against §§1–8: **no weakening or contradiction found.**
- ADR-001 FastAPI — exactly the decision §2 delegated to ADR-001; Flask-elsewhere recorded.
- ADR-002 Qwen3.6-35B-A3B supersession — swaps the *exemplar* of "Qwen3-32B-class", explicitly flagged "same intent"; trigger/process of §3 untouched. Apache-2.0, INT4-on-24 GB, vLLM guided decoding all match §3's parameters.
- ADR-003/004/005/010 — strengthen §6 (transactional enqueue, DB-enforced immutability, no-partial-draft, outbox).
- ADR-006 — honors §2 bundle rules; React 19.2.
- ADR-007 — sandbox stricter than §4's floor; 'unsafe-inline' inside the opaque-origin frame grants nothing §4 forbids.
- ADR-008/009/011/013 — strengthen §4 (RLS, dual-valid rotation, identity-free adapter types, adapter-layer enforcement).
- ADR-012 — enforces §5 (MinIO/AGPL exclusion) with the L2 interpretation note.
- Build rules — all additive (CI contracts, closed event taxonomy, accessibility-preserving sanitiser, config-not-constants, LMS-agnostic edge).
- §9's own framing ("Additive only; pending sign-off; binding once signed") is consistent with the file's status line.

## Six V3 seams (§6 / brief §10) — preserved as stated

| Seam | Preserved via | Verdict |
| --- | --- | --- |
| (a) New block types via player block registry | `BlockRegistry` + schema minor bump (AD-2/AD-10) | PASS |
| (b) Delivery abstraction interface-compatible w/ streaming | `LessonDeliverySource` async block-iterator (AD-10) | PASS |
| (c) Narration provider interface | `NarrationProvider` registry (AD-10) | PASS |
| (d) Generic quota/budget subsystem | `action_type` policy vocabulary, reserve→settle (AD-8/ADR-013) | PASS |
| (e) Static self-containable published assets | Publish freeze into `v{n}/` + manifest + host-free IIFE (AD-9/AD-11) | PASS |
| (f) LMS-agnostic API, Moodle confined to plugin | AD-16 + pull-ack outbox + integrations docs | PASS |

Nothing V3 is built ahead of need (Deferred table confirms); no seam painted over.

## Licence audit (every named package in the stack / task list)

| Package | Licence | Verdict |
| --- | --- | --- |
| FastAPI | MIT | OK |
| uvicorn | BSD-3 | OK |
| Pydantic | MIT | OK |
| SQLAlchemy / Alembic | MIT / MIT | OK |
| Procrastinate | MIT | OK |
| PostgreSQL | PostgreSQL License (BSD-like) | OK |
| jsonschema (py) | MIT | OK |
| openai SDK | Apache-2.0 | OK |
| httpx | BSD-3 | OK (maintenance status separately flagged in spine — good) |
| Playwright | Apache-2.0 | OK (note: runtime dep via pre-publish checks, still permissive) |
| React / react-dom | MIT | OK |
| Preact (option) | MIT | OK |
| Vite | MIT | OK |
| Three.js (+ DRACOLoader/Draco decoder) | MIT (+ Apache-2.0 Draco) | OK |
| **@gltf-transform/cli 4.x** | **Prosperity PPL 3.0 / commercial (CLI only; SDK pkgs stay MIT)** | **VIOLATION → C1** |
| ajv | MIT | OK |
| DOMPurify | Apache-2.0 OR MPL-2.0 (dual) | OK via Apache-2.0 |
| defusedxml | PSF-2.0 | OK (but absent from Stack table → M1) |
| lxml | BSD-3 | n/a — not used anywhere in the deliverable |
| nginx / certbot | BSD-2 / Apache-2.0 | OK |
| SeaweedFS (noted option) | Apache-2.0 | OK |
| Qwen3.6-35B-A3B / vLLM (migration path) | Apache-2.0 / Apache-2.0 | OK |
| Inter / Plus Jakarta Sans (showcase) | SIL OFL 1.1 | OK-compatible → L7 (record it) |

---

## Sign-off gate

Before stakeholder sign-off of the 2026-07-17 run: resolve **C1** (swap or license gltf-transform CLI) and **H1** (land the no-TypeScript rule + CI gate). M1/M2 are one-line edits that should ride the same batch. Lows are notes for §9/spine polish, none blocking.
