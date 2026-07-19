# External Interface: edon-rag Retrieval API (v1.1)

**Status:** final (stakeholder sign-off 2026-07-18)
**System:** edon-rag (existing production RAG backend — FastAPI, PostgreSQL + pgvector, Ollama `nomic-embed-text`, multi-tenant, per-tenant API keys; deployed API version **v2.0.0**, reconciled against its captured `openapi.json` by the stakeholder, 2026-07-18)
**Posture:** edon-rag is an external system consumed **by API only**. This document specifies the contract **this platform requires**. Capabilities listed under *Integration Work Items* are gaps to be built on the edon-rag side as explicit, ticketed work — never assumed edits. v1.1 supersedes v1 (which assumed a tenant-wide retrieval endpoint and Bearer auth; both corrected below).

## 1. Reconciliation summary (v1 → v1.1)

| # | Finding from the deployed `openapi.json` (v2.0.0) | Contract consequence |
| --- | --- | --- |
| 1 | **No retrieval-only endpoint exists.** The only query surface is the chat pipeline (`POST /api/courses/{id}/query`), which generates an answer — unusable for grounding (it spends chat-pipeline inference and returns prose, not ranked chunks). | **WI-RAG-0 (Critical, blocks generation epics):** a raw-retrieval endpoint must be built edon-rag-side. Specified in §3. |
| 2 | Auth is an **`x-api-key` header**, not `Authorization: Bearer`. | Corrected throughout; the platform sends `x-api-key: <tenant-key>`. |
| 3 | The production corpus is **course-scoped by `moodle_course_id`** — there is no tenant-wide collection to query. | The retrieval endpoint is course-scoped (§3). Course scope comes from the Launch Token (Teacher generation) or the chat's course context (Diagram Requests). Tenant-wide retrieval is not the primary mode; **WI-RAG-2 (tag filtering) is deferred to roadmap**, and Curriculum Reference derivation uses its topic-derived fallback (handoff item 12 fallback is now the primary mechanism). |
| 4 | Document titles are embedded per chunk at ingestion; stable ids are achievable. Positional locators are not present for existing corpora. | **WI-RAG-1 amended:** `chunk_id`/`document_id`/`document_title` are required response fields (achievable); `locator` is **nullable** — captured for newly ingested documents only; **no re-ingestion of existing corpora**. Citations degrade to excerpt + document title per the approved fallback (already the schema's required set — AD-2). |
| 5 | Production declares **no response models** (all 200s are empty schemas). | **WI-RAG-3:** the new retrieval endpoint must declare typed response models in its OpenAPI spec. |
| 6 | `max_documents_per_course` defaults to **5**. | Operational note, not contractual: per-tenant raises may be needed for grounding quality; monitor via generation-quality telemetry (SM-2). |

## 2. Consumers, auth, and scoping

| Platform consumer | Purpose | Scope source |
| --- | --- | --- |
| Generation pipeline | Grounding Chunks for lesson generation (FR-4, FR-6) | `course_ref` from the Launch Token, mapped to `moodle_course_id` |
| Diagram service | Grounding for Student Diagram Requests (FR-19, FR-28) | course context supplied by block_edon_ai (required — see that contract) |

- **Auth:** `x-api-key: <tenant-api-key>` per request (edon-rag's existing convention). The key is the tenant boundary; the course id selects a corpus **within** that tenant — edon-rag must reject a course id not belonging to the key's tenant (404/403, never cross-tenant data).
- **No user identity crosses this boundary** (NFR-9): requests carry only the key, the course id, the query text, and retrieval parameters.
- Timeouts: 15 s deadline; timeout = retrieval failure (Generation Job fails `ungrounded` per A-5 after one retry; Diagram Request returns the user-facing failure outcome).

## 3. Required endpoint — WI-RAG-0 (to be built)

### `POST /api/courses/{moodle_course_id}/retrieve`

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

Response `200` (typed model required — WI-RAG-3):

```json
{
  "chunks": [
    {
      "chunk_id": "stable-opaque-id",
      "document_id": "stable-opaque-id",
      "document_title": "NCE Physics Curriculum — Year 2",
      "locator": null,
      "text": "…chunk text…",
      "score": 0.83
    }
  ]
}
```

| Field | Required | Notes |
| --- | --- | --- |
| `chunk_id`, `document_id` | yes, stable | Citations persist inside immutable Published Versions (I-3); ids must stay stable across re-indexing. |
| `document_title` | yes | Embedded per chunk at ingestion — confirmed achievable. |
| `locator` | **nullable** | Newly ingested documents only; existing corpora return `null` (no re-ingestion). The Lesson Script citation object already treats it as optional (AD-2). |
| `text` | yes | Prompt grounding + stored Citation excerpt — Published Versions never depend on edon-rag availability (NFR-4). |
| `score` | yes | Ranking, ungrounded-detection threshold (A-5), telemetry. |

Errors: `401/403` (bad/revoked key), `403/404` (course not in the key's tenant), `422` (malformed), `429` (backoff), `5xx` (one retry, then visible failure). Never surfaced raw to users.

## 4. Non-requirements (explicitly out of contract)

- **Embeddings:** stay inside edon-rag (`nomic-embed-text` via Ollama); the platform never requests raw embeddings; the platform's `embeddings` workload key exists in config for completeness only.
- **Indexing/ingestion:** remains edon-rag's and the institutions' concern. **No re-ingestion of existing corpora is required by this contract.**
- **Chat/answer generation:** the platform brings its own LLM adapter; the retrieval endpoint must not generate.
- **User identity:** never sent (NFR-9).

## 5. Integration Work Items (edon-rag-side, ticketed)

| ID | Work | Priority | Blocks |
| --- | --- | --- | --- |
| **WI-RAG-0** | Build `POST /api/courses/{moodle_course_id}/retrieve` (raw retrieval, no generation), `x-api-key`-authed, course-in-tenant enforced, per §3. | **Critical** | **Generation epics** (M1's live-retrieval slice; recorded fixtures unblock pipeline development meanwhile). |
| **WI-RAG-1** (amended) | Stable `chunk_id`/`document_id` + per-chunk `document_title` in the retrieval response; `locator` nullable, populated for new ingestions only. | High (part of WI-RAG-0's definition of done) | Same as WI-RAG-0. |
| **WI-RAG-3** | Declared response models on the new endpoint (production currently declares none). | Medium (part of WI-RAG-0's DoD) | Contract testability. |
| **WI-RAG-2** | Metadata/tag filtering for curriculum scoping. | **Deferred to roadmap** | Nothing — course scoping covers MVP; Curriculum Reference uses the topic-derived fallback. |

Operational (not contractual): review `max_documents_per_course` (default 5) per tenant if grounding quality telemetry indicates starvation.
