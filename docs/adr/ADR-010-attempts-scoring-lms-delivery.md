# ADR-010: Attempts, Scoring, and LMS Delivery

**Status:** Proposed (pending stakeholder sign-off, architecture run 2026-07-17)

## Context
UX handoff items 11 (attempt unit incl. cross-version "highest attempt") and 17 (quiz submission durability); FR-15 (server-authoritative scoring), FR-23/OQ-15 (completion, retakes, highest attempt, version pinning), A-13 (retriable writeback), SM-3 (24 h window), A-4 (in-flight sessions keep their version).

## Decision

**Attempt unit — an attempt is one full Lesson run pinned to one Published Version, scoped to `(lesson_id, activity_ref)`** (the same Lesson placed in two activities has independent attempts, limits, and completion — AD-15).
- Created lazily and **consumed only at the first Quiz submission** of a run: view-only browsing never spends an attempt; a Lesson with no Quiz Blocks has unlimited runs (attempt limits are quiz-protecting by nature).
- **Reload/resume:** run state (viewed marks, submitted quiz state, pinned version, position) is server-persisted per `(student, lesson)` keyed to the open attempt and restored by the playback session (`resume` block in the session response). A reload re-attaches; it never ends the pinned session and never consumes an attempt (UX Player-reloaded state).
- **Retake:** explicit post-completion action; new attempt pins the **latest** Published Version; allowed while `attempts_used < limit` (limit configured in the Moodle Lesson picker, passed per playback session).
- **Cross-version scoring:** every attempt scores `earned / possible` against **its own version's** quiz denominator, stored as a fraction. "Highest attempt" = max fraction across the Lesson's attempts regardless of version; the gradebook receives `best_fraction × grademax`. Attempt counts are **per-Lesson**, not per-version (UX Completion summary rule). The completion summary's "best score so far" line reads the same fraction.

**Quiz submission durability (single-fire, at-most-once).**
- The client generates a `submission_uuid` per Submit tap; the endpoint is idempotent on `(attempt_id, block_id, submission_uuid)` — retries return the original result, so an attempt is consumed at most once per Submit regardless of network retries.
- The server re-scores deterministically against the pinned Published Version (FR-15/OQ-4 normalised matching) and persists submission + score + the grade/completion **outbox rows in one PostgreSQL transaction before acking**. "Saving your score…" renders only on ack (durable acceptance — UX item 17); until then the "don't close" state.
- Unacked submissions persist in a client localStorage outbox, retried on interval and flushed via `sendBeacon` on pagehide.

**LMS delivery — the outbox (V3 seam f).**
- `delivery_outbox` rows (`kind: grade | completion`, idempotent delivery ids) written transactionally with the facts they report. mod_edonlesson drains via scheduled-task **pull + ack-with-status** (docs/integrations/mod-edonlesson §2.4, Task API verified current): each delivery is acked `applied` or `failed {error_code}` — a failed ack emits the platform `writeback_failure` event; the row survives and its redelivery on the next run emits `writeback_retry` (so FR-27's "writeback failure and retry" events are real, not inferred); a row aging past the 24 h SM-3 window emits `writeback_overdue` (monitoring config).
- Completion fires when all renderable Blocks are viewed and all Quiz Blocks submitted (OQ-15; unknown types excluded per FR-2).

## Consequences
- The platform is the system of record for attempts and scores; Moodle is a projection. LTI 1.3 later consumes the same outbox.
- Formative-stakes posture (A-21) unchanged: client feedback instant, server score authoritative.
- Abandoned open attempts (started, never completed) persist harmlessly; a retake is only offered post-completion, so an abandoned run resumes rather than multiplying attempts.
