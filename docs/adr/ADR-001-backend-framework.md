# ADR-001: Backend Framework — FastAPI

**Status:** Accepted (stakeholder sign-off, 2026-07-18)
**Reserved by:** project-context.md §2/§8; brief §9; PRD addendum §1.

## Context

Team standard for new microservices is Flask; the adjacent production service edon-rag is FastAPI. Either is acceptable; silence is not. The workloads that decide it:

- The generation pipeline is queued, asynchronous, and LLM-bound (FR-8): long-lived outbound HTTP calls to LLM providers and edon-rag, many concurrent, ideal for asyncio.
- Progress feedback (per-Block generation progress events, UX amendment E) wants SSE/long-poll — natively comfortable on ASGI.
- The Lesson Script Schema is the product spine (I-3); Pydantic v2 models + JSON Schema are first-class in FastAPI, and the platform API must ship an accurate OpenAPI description because it is a versioned external interface consumed by two companion plugins (docs/integrations/).
- Verified 2026-07-17: FastAPI 0.139.2 (active, Pydantic v2 native, tested through Python 3.14); Flask 3.1.3 (stable but WSGI; `flask[async]` still ties one worker per request — Pallets docs steer heavy-async work to Quart).

## Decision

**FastAPI** (0.139.x at cold-start), served by uvicorn under systemd, for the single backend application and its worker processes. All platform services follow this uniformly (there is exactly one backend deployable — the modular monolith — plus workers importing the same core).

## Consequences

- Async-first core: LLM adapter, edon-rag client, and pipeline stages are `async`; the job queue must be asyncio-native (see ADR-003).
- Pydantic v2 models mirror (never replace) the canonical JSON Schema documents in `/schema` — the JSON Schema files remain the single source of truth (I-3); a CI check asserts the Pydantic mirrors validate identically against the schema fixtures.
- OpenAPI is generated and published for the platform API; docs/integrations/ contracts reference it.
- Team standard divergence is deliberate and recorded: Flask remains the team default elsewhere; this repo is FastAPI end-to-end, consistent with edon-rag operational experience.
- Blast radius if wrong: the hexagonal core keeps domain logic framework-free; routers/DI are the only FastAPI-coupled layer.
