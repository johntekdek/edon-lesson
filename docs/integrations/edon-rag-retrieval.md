# External Interface: edon-rag Retrieval API (v1)

**Status:** draft — pending stakeholder sign-off of the architecture run 2026-07-17
**System:** edon-rag (existing production RAG backend — FastAPI, PostgreSQL + pgvector, Ollama `nomic-embed-text`, multi-tenant, per-tenant API keys)
**Posture:** edon-rag is an external system consumed **by API only**. This document specifies the contract **this platform requires**, versioned as interface `v1`. Any capability listed under *Integration Work Items* is a gap to be negotiated with the edon-rag owners as explicit work — never an assumed edit to edon-rag. Changes to what we need bump this document's version.

## 1. Consumers and purposes

| Platform consumer | Purpose | PRD anchor |
| --- | --- | --- |
| Generation pipeline (plan + per-Block stages) | Retrieve Grounding Chunks for lesson generation, Tenant-scoped | FR-4, FR-6 |
| Diagram service | Retrieve Grounding Chunks for Student Diagram Requests (mandatory grounding) | FR-19, FR-28 |

Both consumers call server-side from the platform backend. **No Student or Teacher identity is ever forwarded to edon-rag** — requests carry only the tenant credential, the query text, and retrieval parameters (NFR-9 identity-stripping happens before this boundary).

## 2. Authentication and tenant scoping

- Per-tenant API key in a request header (`Authorization: Bearer <tenant-api-key>` or edon-rag's existing header convention — adopt whichever edon-rag already uses; the platform stores one edon-rag credential per Tenant in tenant config, encrypted at rest).
- The API key **is** the tenant scope: retrieval must return chunks exclusively from that tenant's Corpus. The platform never passes a tenant identifier in the body; cross-tenant retrieval must be impossible by construction on the edon-rag side (this matches edon-rag's existing multi-tenant model).
- Timeouts: platform calls with a 15 s deadline and treats timeout as a retrieval failure (Generation Job fails as ungrounded per A-5 if no usable chunks are obtained after retry; Diagram Request fails with the user-facing "couldn't produce that diagram" outcome).

## 3. Required endpoint

### `POST /api/v1/retrieve`

Request (`application/json`):

```json
{
  "query": "Ohm's law and simple circuits — lesson plan grounding",
  "top_k": 8,
  "min_score": 0.0,
  "filters": {
    "document_ids": ["optional — restrict to specific corpus documents"],
    "tags": ["optional — curriculum/subject tags, see WI-RAG-2"]
  }
}
```

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `query` | string | yes | Natural-language retrieval query. ≤ 2,000 chars. |
| `top_k` | int | no (default 8) | Platform uses 6–16 depending on pipeline stage; contract max 32. |
| `min_score` | float | no | Similarity floor; platform default 0 (filtering done platform-side). |
| `filters` | object | no | Optional narrowing. Absence = whole tenant Corpus. See WI-RAG-2. |

Response `200` (`application/json`):

```json
{
  "chunks": [
    {
      "chunk_id": "stable-opaque-id",
      "document_id": "stable-opaque-id",
      "document_title": "NCE Physics Curriculum — Year 2",
      "locator": "Section 4.3, p. 87",
      "text": "…chunk text…",
      "score": 0.83,
      "metadata": {
        "tags": ["physics", "electricity"],
        "source_type": "curriculum|handbook|notes",
        "indexed_at": "2026-05-02T10:00:00Z"
      }
    }
  ]
}
```

| Field | Required | Why the platform needs it |
| --- | --- | --- |
| `chunk_id` | yes, **stable** | Citations (FR-6) persist inside immutable Published Versions forever (I-3). The id must remain resolvable (or at least stable as an identifier) across edon-rag re-indexing. See WI-RAG-1. |
| `document_id`, `document_title` | yes | Citation display in the Review Workspace and Player Sources section (OQ-10). |
| `locator` | strongly desired | Human-readable position (section/page). Displayed on Citation cards. See WI-RAG-1. |
| `text` | yes | Prompt grounding + Citation excerpt (platform stores the excerpt with the Citation, so Published Versions never depend on edon-rag availability — NFR-4). |
| `score` | yes | Ranking, ungrounded-detection threshold (A-5), telemetry. |
| `metadata.tags` | desired | Curriculum Reference derivation (UX handoff item 12) and future course-scoped filtering. See WI-RAG-2. |

Errors: `401/403` (bad/revoked key), `422` (malformed request), `429` (edon-rag-side rate limiting, if any — platform backs off), `5xx` (platform retries once, then fails the consuming operation visibly). Error bodies are logged tenant-scoped; never surfaced raw to users.

### Optional: `GET /api/v1/health`
Unauthenticated or key-authenticated liveness probe used by platform ops monitoring. If absent, the platform treats retrieval errors as the only signal (acceptable; listed for completeness, not required).

## 4. Non-requirements (explicitly out of contract)

- **Embeddings**: the `embeddings` workload stays inside edon-rag (`nomic-embed-text` via Ollama) exactly as today; the platform never requests raw embeddings.
- **Indexing/ingestion**: corpus management remains edon-rag's and the institutions' concern; the platform only reads.
- **Chat/completion**: the platform brings its own LLM adapter; edon-rag is retrieval-only in this contract.
- **Student identity**: never sent (NFR-9).

## 5. Integration Work Items (gaps — to verify against production edon-rag, never assumed)

| ID | Requirement | If absent, MVP fallback | Priority |
| --- | --- | --- | --- |
| **WI-RAG-1** | Stable `chunk_id`/`document_id`, `document_title`, and a human-readable `locator` in retrieval responses (citation-grade metadata). | Platform stores the full excerpt + whatever metadata exists at generation time; Citations degrade to excerpt + document title without deep locators. Published lessons remain self-contained either way. | **High — verify first.** The brief promises "ranked chunks with metadata/citations"; the exact fields must be confirmed against the deployed API. |
| **WI-RAG-2** | Metadata/tag filtering (`filters.tags`) usable for curriculum/subject scoping. | Tenant-wide retrieval only (still satisfies FR-4, which requires Tenant scoping, not course scoping); Curriculum Reference derivation falls back to topic-derived labels (handoff item 12 fallback). | Medium |
| **WI-RAG-3** | `top_k` and `min_score` request parameters honored. | Platform truncates/filters client-side from whatever fixed count edon-rag returns. | Low |
| **WI-RAG-4** | Documented error semantics + a 429 backoff signal. | Platform treats all non-200 as retriable-once failures. | Low |

**First action when integration work starts:** capture the deployed edon-rag OpenAPI spec (it is FastAPI — `/openapi.json` exists) and reconcile this contract against it; convert every mismatch into a ticketed work item under the IDs above.
