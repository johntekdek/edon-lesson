# External Interface: edon-rag Retrieval API (v1.2)

**Status:** final — v1.2 signed off by john 2026-07-18 (delivery + error-convention update; `metadata` additive-field rule, `document_ids` filter adoption, and the chunk-id stability note ratified at the implementation-readiness sign-off). v1.1 was final, stakeholder sign-off 2026-07-18.
**System:** edon-rag (existing production RAG backend — FastAPI, PostgreSQL + pgvector, Ollama `nomic-embed-text`, multi-tenant, per-tenant API keys; deployed API version **v2.1.0**, which includes the WI-RAG-0 retrieval endpoint; v1.1 was reconciled against v2.0.0's captured `openapi.json` by the stakeholder, 2026-07-18)
**Posture:** edon-rag is an external system consumed **by API only**. This document specifies the contract **this platform requires**. Capabilities listed under *Integration Work Items* are gaps to be built on the edon-rag side as explicit, ticketed work — never assumed edits. v1.1 superseded v1 (which assumed a tenant-wide retrieval endpoint and Bearer auth). v1.2 supersedes v1.1: **WI-RAG-0/-1 delivered** (edon-rag v2.1.0, 2026-07-18, 45 edon-rag-side tests; recorded fixtures committed at `fixtures/edon-rag/`); **locator support is FULL for existing corpora** (per-chunk `page_number` already existed at ingestion — the v1.1 "no positional locators for existing corpora" finding was wrong); and **a course not owned by the key's tenant returns `404`** (not 401/403 — edon-rag convention), corrected in §2/§3.

## 1. Reconciliation summary (v1 → v1.1)

> Historical record — rows are the v1→v1.1 reconciliation as found against v2.0.0. §1.1 records the v1.2 delivery update, which supersedes rows 1 and 4.

| # | Finding from the deployed `openapi.json` (v2.0.0) | Contract consequence |
| --- | --- | --- |
| 1 | **No retrieval-only endpoint exists.** The only query surface is the chat pipeline (`POST /api/courses/{id}/query`), which generates an answer — unusable for grounding (it spends chat-pipeline inference and returns prose, not ranked chunks). | **WI-RAG-0 (Critical, blocks generation epics):** a raw-retrieval endpoint must be built edon-rag-side. Specified in §3. |
| 2 | Auth is an **`x-api-key` header**, not `Authorization: Bearer`. | Corrected throughout; the platform sends `x-api-key: <tenant-key>`. |
| 3 | The production corpus is **course-scoped by `moodle_course_id`** — there is no tenant-wide collection to query. | The retrieval endpoint is course-scoped (§3). Course scope comes from the Launch Token (Teacher generation) or the chat's course context (Diagram Requests). Tenant-wide retrieval is not the primary mode; **WI-RAG-2 (tag filtering) is deferred to roadmap**, and Curriculum Reference derivation uses its topic-derived fallback (handoff item 12 fallback is now the primary mechanism). |
| 4 | Document titles are embedded per chunk at ingestion; stable ids are achievable. Positional locators are not present for existing corpora. | **WI-RAG-1 amended:** `chunk_id`/`document_id`/`document_title` are required response fields (achievable); `locator` is **nullable** — captured for newly ingested documents only; **no re-ingestion of existing corpora**. Citations degrade to excerpt + document title per the approved fallback (already the schema's required set — AD-2). |
| 5 | Production declares **no response models** (all 200s are empty schemas). | **WI-RAG-3:** the new retrieval endpoint must declare typed response models in its OpenAPI spec. |
| 6 | `max_documents_per_course` defaults to **5**. | Operational note, not contractual: per-tenant raises may be needed for grounding quality; monitor via generation-quality telemetry (SM-2). |

## 1.1 Delivery update (v1.1 → v1.2, 2026-07-18)

- **WI-RAG-0 COMPLETE.** `POST /api/courses/{moodle_course_id}/retrieve` is implemented, tested (45 edon-rag-side tests), and deployed as **edon-rag v2.1.0**. Real recorded responses from the production endpoint are committed at `fixtures/edon-rag/` (`01_basic_query.json`, `02_top_k_and_min_score.json`, `03_document_ids_filter.json`).
- **WI-RAG-1 closed at full strength.** Per-chunk `page_number` already existed for existing corpora, so `locator` is populated for them too (page-based string, e.g. `"Page 6"`) — the v1.1 assumption that positional locators required re-ingestion was wrong. `locator` stays nullable in the schema so the approved citation fallback (AD-2) remains valid for any future locator-less source.
- **Error-convention correction.** A course id not owned by the key's tenant returns **`404`** — not 401/403 — matching edon-rag conventions (ownership failure is indistinguishable from not-found; existence never leaks cross-tenant).
- **WI-RAG-3** was part of WI-RAG-0's definition of done and is delivered with it (confirmed at sign-off 2026-07-18; platform-side verification of the typed response models lands at Story 2.7's staging smoke).
- Consequence for planning artifacts: **Epic 2's live-switch story (2.7) is no longer blocked-external.**

## 2. Consumers, auth, and scoping

| Platform consumer | Purpose | Scope source |
| --- | --- | --- |
| Generation pipeline | Grounding Chunks for lesson generation (FR-4, FR-6) | `course_ref` from the Launch Token, mapped to `moodle_course_id` |
| Diagram service | Grounding for Student Diagram Requests (FR-19, FR-28) | course context supplied by block_edon_ai (required — see that contract) |

- **Auth:** `x-api-key: <tenant-api-key>` per request (edon-rag's existing convention). The key is the tenant boundary; the course id selects a corpus **within** that tenant — edon-rag rejects a course id not belonging to the key's tenant with **`404`** (edon-rag convention: ownership failure is indistinguishable from not-found; never cross-tenant data, never 401/403 for ownership).
- **No user identity crosses this boundary** (NFR-9): requests carry only the key, the course id, the query text, and retrieval parameters.
- Timeouts: 15 s deadline; timeout = retrieval failure (Generation Job fails `ungrounded` per A-5 after one retry; Diagram Request returns the user-facing failure outcome).

## 3. Endpoint — WI-RAG-0 (**delivered**, edon-rag v2.1.0)

### `POST /api/courses/{moodle_course_id}/retrieve`

Delivered behaviour is captured in recorded fixtures at `fixtures/edon-rag/`, recorded from the production v2.1.0 endpoint (`01_basic_query`, `02_top_k_and_min_score`, `03_document_ids_filter`).

Request (`application/json`):

```json
{
  "query": "Ohm's law and simple circuits — lesson plan grounding",
  "top_k": 8,
  "min_score": 0.0
}
```

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `query` | string | yes | ≤ 2,000 chars. Retrieval only — the endpoint must perform **no answer generation** (no chat-pipeline LLM spend). |
| `top_k` | int | no (default 8) | Platform uses 6–16 by pipeline stage; contract max 32. |
| `min_score` | float | no | Platform default 0 (filters platform-side). |
| `document_ids` | array[string] | no | Optional filter restricting retrieval to the given `document_id`s within the course corpus. Implemented and tested in v2.1.0; **adopted into the contract at sign-off 2026-07-18** (fixture 03). Not a platform dependency — no MVP pipeline stage requires it. |

Response `200` (typed model required — WI-RAG-3):

```json
{
  "chunks": [
    {
      "chunk_id": "stable-opaque-id",
      "document_id": "stable-opaque-id",
      "document_title": "NCE Physics Curriculum — Year 2",
      "locator": "Page 6",
      "text": "…chunk text…",
      "score": 0.83
    }
  ]
}
```

| Field | Required | Notes |
| --- | --- | --- |
| `chunk_id`, `document_id` | yes | **Stability note (stakeholder-confirmed 2026-07-18):** ids are DB row ids — stable in normal operation, but they may change if a document is deleted and re-uploaded; this is accepted. Citation integrity inside immutable Published Versions (I-3) is guaranteed by the **stored excerpt + `document_title`** (AD-2's required citation set), never by id dereference back to edon-rag. |
| `document_title` | yes | Embedded per chunk at ingestion — confirmed achievable. |
| `locator` | **nullable** | **Populated for existing corpora too** (v1.2): a page-based string (e.g. `"Page 6"`) from per-chunk `page_number` captured at ingestion — no re-ingestion was needed. Stays nullable so the citation fallback (AD-2) remains valid for any future locator-less source. |
| `text` | yes | Prompt grounding + stored Citation excerpt — Published Versions never depend on edon-rag availability (NFR-4). |
| `score` | yes | Ranking, ungrounded-detection threshold (A-5), telemetry. |
| `metadata` | no (additive) | **Allowed additive object** (sign-off 2026-07-18): chunks may carry extra keys under `metadata` (e.g. `indexed_at` in the v2.1.0 fixtures). Consumers and fixture-shape tests validate the required set strictly and **tolerate additive `metadata` keys** — never depend on them. |

Errors: `401/403` (bad/revoked key), `404` (course not in the key's tenant, or nonexistent — edon-rag convention, corrected in v1.2; ownership failures are never 401/403), `422` (malformed), `429` (backoff), `5xx` (one retry, then visible failure). Never surfaced raw to users.

## 4. Non-requirements (explicitly out of contract)

- **Embeddings:** stay inside edon-rag (`nomic-embed-text` via Ollama); the platform never requests raw embeddings; the platform's `embeddings` workload key exists in config for completeness only.
- **Indexing/ingestion:** remains edon-rag's and the institutions' concern. **No re-ingestion of existing corpora is required by this contract.**
- **Chat/answer generation:** the platform brings its own LLM adapter; the retrieval endpoint must not generate.
- **User identity:** never sent (NFR-9).

## 5. Integration Work Items (edon-rag-side, ticketed)

| ID | Work | Status | Blocks |
| --- | --- | --- | --- |
| **WI-RAG-0** | Build `POST /api/courses/{moodle_course_id}/retrieve` (raw retrieval, no generation), `x-api-key`-authed, course-in-tenant enforced, per §3. | **COMPLETE** — deployed as edon-rag v2.1.0, 45 tests, fixtures committed (2026-07-18). | Nothing — Story 2.7 (live-retrieval switch) is unblocked. |
| **WI-RAG-1** | Stable `chunk_id`/`document_id` + per-chunk `document_title` in the retrieval response; `locator` nullable. | **COMPLETE at full strength** — `locator` populated for existing corpora too (per-chunk `page_number` existed at ingestion). | Nothing. |
| **WI-RAG-3** | Declared response models on the new endpoint (production previously declared none). | **Complete per WI-RAG-0's DoD** (confirmed at sign-off 2026-07-18). | Nothing (platform-side verification at 2.7's staging smoke). |
| **WI-RAG-2** | Metadata/tag filtering for curriculum scoping. | **Deferred to roadmap** (unchanged) | Nothing — course scoping covers MVP; Curriculum Reference uses the topic-derived fallback. |

Operational (not contractual): review `max_documents_per_course` (default 5) per tenant if grounding quality telemetry indicates starvation.
