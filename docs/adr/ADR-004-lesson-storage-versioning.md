# ADR-004: Lesson Storage and Versioning Model

**Status:** Accepted (stakeholder sign-off, 2026-07-18)

## Context
FR-7/FR-11/I-3: Drafts and immutable Published Versions coexist; republishing creates a new version; published lessons remain playable forever and never depend on LLM or edon-rag availability (NFR-4). Creator-owns model (OQ-13). Autosave durability (UX Block-editor rule).

## Decision
PostgreSQL is the system of record; Lesson Scripts are stored as JSONB validated against the `/schema` package before every write (FR-3).

- `lessons` — identity + ownership: `(id, tenant_id, course_ref, topic, owner_user_id, created_at)`. The Lesson is the versioning umbrella (attempt counts and SM-2 both key on it).
- `drafts` — one **mutable** working Draft per Lesson (`lesson_id` unique): `script` JSONB, `updated_at`, `revision` (monotonic int for optimistic concurrency — the Authoring UI sends `If-Match: revision`; mismatch = 409, never silent overwrite). Autosave = partial-update endpoints (block-level patch) that revalidate the whole script server-side before commit; a failed validation returns field-pinned errors and does not persist (UX Draft-validation state).
- `published_versions` — **immutable**: `(lesson_id, version_no)` unique, full `script` JSONB (citations embedded), `schema_version`, `asset_manifest` JSONB, `published_at`, `published_by`. No UPDATE/DELETE grants on this table for the app role — immutability is enforced by the database, not convention. Publishing = a short, progress-visible publish job: revalidate Draft → run pre-publish checks (FR-17/A-35) → generate TTS audio for changed Narration Blocks (`tts` workload; per-Block text hash — republish regenerates only changed audio; stakeholder amendment 2026-07-18) → freeze assets incl. audio (ADR-012) → final transaction asserting the checked `revision` unchanged (AD-23) → insert version row → emit `lesson_published` event.
- `citations` are also projected to a queryable table `(version_id, block_id, chunk_id, document_id, document_title, locator, excerpt)` for review UI and telemetry; the embedded JSONB copy inside the script is what makes the Published Version self-contained.
- Draft discard = delete `drafts` row + `draft_discarded` event; the Lesson row and any Published Versions survive.
- Duplicate-as-my-draft (OQ-13): copies a Published Version's script into a **new Lesson** owned by the duplicating Teacher (provenance field `duplicated_from_version_id`).

## Consequences
- Idempotency privacy (OQ-13): the `request_fingerprint` unique index is scoped **per (tenant, owner)** — Drafts are creator-private, so two Teachers submitting the same normalised request each get their own Draft; the fingerprint guards *accidental resubmission by the same Teacher*, nothing more. Fingerprint = SHA-256 over (tenant, owner, course_ref, normalised topic + guidance, schema major, pipeline config version), using the shared normaliser (Unicode NFC → casefold → whitespace collapse → trim → strip trailing punctuation).
- Scripts reference assets as `asset://{asset_id}`; delivery resolves ids against live paths (Drafts) or the frozen manifest (Published Versions), so publish never alters the script bytes the Teacher previewed (FR-9).
- Glossary note: the PRD's "version history of Drafts" is realised as one mutable Draft whose autosave `revision` sequence is the draft history; distinct co-existing Drafts per Lesson are not an MVP requirement (UX shows a single Draft per Lesson card).
- Lesson metadata carries `curriculumRef: {value, source: pipeline|teacher}` — derived in the plan stage, Teacher-correctable in the Review Workspace metadata header (UX handoff item 12); the pipeline value is retained when overridden.
- "Latest wins for new sessions" (A-4) is a `MAX(version_no)` read; version pinning is a foreign key on the attempt (ADR-010).
- Idempotency cache for generation (A-7) is a unique index on `drafts.request_fingerprint` per tenant.
- Republishing never rewrites history: gradebook/completion records reference `published_version_id` forever.
- Storage growth is bounded and cheap (JSONB scripts are ~10–100 KB; assets live in the object store).
