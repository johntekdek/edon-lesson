# ADR-003: Job Queue — Procrastinate (PostgreSQL-backed)

**Status:** Proposed (pending stakeholder sign-off, architecture run 2026-07-17)

## Context

Generation Jobs are queued and async (FR-8, project-context §6); the grade/completion outbox and writeback retries need durable, transactional job state (SM-3); the ops envelope is a single VPS with nginx/systemd and PostgreSQL already present, scaling generation workers horizontally later. Verified 2026-07-17: Celery 5.6.3 (requires Redis/RabbitMQ broker), RQ 2.10 (Redis), Dramatiq 2.2 (Redis/RabbitMQ), arq 0.28 (**maintenance-only**), Procrastinate 3.9.0 (PostgreSQL 13+, async-native, retries/locks/periodic tasks, active 2026 cadence; caveat: maintainers seeking help — steady releases, bus-factor noted), pgqueuer 1.2 (younger, smaller).

## Decision

**Procrastinate 3.x** on the platform PostgreSQL instance. No Redis/RabbitMQ in the stack.

- Jobs enqueue **in the same transaction** as their domain writes (draft rows, outbox rows, quiz-submission acks) — this transactional-enqueue property is load-bearing for the durability decisions (quiz submission durability, grade outbox) and is what a broker-based queue cannot give without outbox scaffolding of its own.
- Async-native workers match the FastAPI/asyncio core (ADR-001).
- Workers run as separate systemd services importing the same core package; horizontal scaling = more worker hosts pointing at the same PostgreSQL (satisfies project-context §2 "design workers to scale horizontally later").
- Queue names per workload (`generation`, `delivery`, `maintenance`); per-queue concurrency config; Budget-Ceiling pause = pausing intake on `generation` (jobs already fetched run to completion, per A-29/FR-26).

## Consequences

- PostgreSQL is the single stateful service to operate and back up (with the filesystem asset store) — matches team ops practice.
- Bus-factor mitigation: task definitions are thin wrappers over core use-case functions (hexagonal), so a queue swap (pgqueuer, Celery) touches only the worker adapter layer; no domain logic imports Procrastinate.
- Queue throughput ceiling is PostgreSQL's — irrelevant at ~60-tenant generation volumes (tens of jobs/hour, not thousands/second).
- Progress events: per-Block progress is written to a `job_progress` table by pipeline stages and streamed to the Authoring UI via SSE/poll; Procrastinate job status supplies only the coarse queued/running/done/failed states (A-8 floor).
