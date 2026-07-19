---
baseline_commit: 473b7531b08c2ee00be94d5a6ab9b0fce1a5952a
---

# Story 1.1: Lesson Script Schema v1.0 Package

Status: done

## Story

As a renderer or pipeline author,
I want the versioned Lesson Script Schema shipped as a first-class validated package with fixtures and documentation,
So that every producer and consumer shares one content contract whose Published Versions stay playable forever.

## Acceptance Criteria

1. **Schema documents (FR-1, AD-2):** Given the freshly bootstrapped monorepo `[ASSUMPTION: this story includes the minimal repo bootstrap /schema needs; the full scaffold is Story 1.2]`, when the `/schema` package is built, then JSON Schema 2020-12 documents define Lesson Script v1.0 (`"schema": "1.0"`) with lesson metadata — tenant, course reference, `curriculumRef {value, source: "pipeline"|"teacher"}`, version, Citations — and an ordered Block list covering all six MVP Block types (Slide, Narration, Quiz, Diagram, Model3D, Simulation).
2. **Pinned payload facts (AD-2, AD-12):** camelCase field casing throughout; Narration Blocks carry optional `audioRef`; Diagram Blocks and Model3D/Simulation posters carry `altText`/`longDescription`; every heavy-asset reference carries `transferSize` in bytes; the citation object requires only `sourceChunkId`, `documentTitle`, `excerpt` with `locator`/`documentId`/`tags` optional; Simulation Blocks define `mode: "template" | "freecode"` with `templateId`/`bundleRef` payload fields.
3. **Fixture corpus + dual validators (FR-1, FR-2):** Given the shared fixture corpus (valid scripts, invalid scripts, an unknown-Block-type fixture, future minor- and major-version fixtures, a no-locator citation fixture), when the `js/` (ajv) and `py/` (jsonschema) validator wrappers run in CI, then both validators agree on every fixture, and a script missing schema version, tenant, or version metadata fails validation.
4. **Version-mismatch semantics documented (A-26):** minor = additive only (ignore unknowns); major = defined cannot-play state applying only to scripts newer than the player build.
5. **Renderer-sufficient docs (FR-3):** Given the package documentation in `/schema/docs`, a renderer author can implement each Block type against the package alone, without pipeline code; the docs carry the version-bump + migration/compatibility-note rule and the reserved-extensions record (V2 dialogue types, V3 streaming — record only, do not design).

## Tasks / Subtasks

- [x] Task 1: Minimal repo bootstrap for `/schema` (AC: 1)
  - [x] Create `schema/` at repo root (this repo IS the primary `edon-lesson` monorepo — `docs/adr`, `docs/integrations`, `fixtures/edon-rag/` already exist at root; do not move them)
  - [x] Root `package.json` with npm workspaces listing `schema/js` (lockfile committed); `schema/py/pyproject.toml` for the Python wrapper `[ASSUMPTION: minimal root files only — no backend/, player/, authoring/ dirs; Story 1.2 owns the full scaffold and `uv` root lockfile]`
  - [x] Minimal CI workflow running only this package's checks `[ASSUMPTION: GitHub Actions — the spine's working assumption; Story 1.2 formally records the CI-provider decision and expands the gate set]`. Interim py-deps install (root `uv` lockfile is 1.2's): CI installs `schema/py` with `uv pip install` against the pyproject pins
- [x] Task 2: Author the JSON Schema 2020-12 documents (AC: 1, 2)
  - [x] Lesson envelope: `schema` (string, **pattern `^\d+\.\d+$` only — never `const`/`enum`**; `"1.0"` is the version this package documents, not a schema constraint — future minors must validate; the major comparison lives in the wrappers, pre-validation), `lessonId`, `tenantId`, `courseRef`, `curriculumRef {value, source}`, `version`, `title`, `language` (BCP-47), ordered `blocks[]`
  - [x] Shared `$defs`: `assetRef {ref: "asset://…", transferSize}`, `citation`, `poster {…, altText, longDescription?}`, base block envelope `{id, type, title, citations[]}`
  - [x] Six per-type block schemas (field shapes in Dev Notes § Block payloads). Strict = required fields + types enforced; **never `additionalProperties: false` / `unevaluatedProperties: false` on block schemas** — AD-2 minor bumps add optional fields to known types, so unknown sibling fields must be tolerated. Unknown block *types* pass via the base-envelope fallback
- [x] Task 3: Build the fixture corpus + expectations manifest (AC: 3)
  - [x] Valid: full six-type lesson; minimal Slide+Quiz lesson (the Epic 2 walking-skeleton shape); Narration with and without `audioRef`; no-locator citation fixture
  - [x] Invalid: missing `schema` / `tenantId` / `version`; block missing `id`; block missing `citations`; block missing `title`; citation missing `excerpt`; Simulation missing `mode`; MC question missing `correctOptionId`; MC question with *dangling* `correctOptionId` (see wrapper semantics note); short-answer with empty `acceptedAnswers`
  - [x] Forward-compat: unknown-Block-type fixture (valid); future-minor `"1.7"` fixture (valid — must contain BOTH an unknown block type AND an unknown extra field on a known block type, so CI mechanically proves the tolerance); future-major `"2.0"` fixture (distinct `unsupportedMajor` outcome); a fixture that is future-major AND schema-invalid (proves the short-circuit rule)
  - [x] `expectations.json` manifest mapping each fixture → expected outcome (`valid | invalid | unsupportedMajor`), consumed by both wrappers
- [x] Task 4: `schema/js` validator wrapper (AC: 3)
  - [x] Plain JavaScript only — a single `.ts`/`.tsx` file is a [HARD] violation; ajv 8.20.x via the `Ajv2020` build (2020-12 dialect); Vitest suite iterating the expectations manifest
- [x] Task 5: `schema/py` validator wrapper (AC: 3)
  - [x] jsonschema 4.26.x `Draft202012Validator`; same API shape as js (`validate(script) → {ok, errors[], unsupportedMajor}`); pytest suite iterating the same manifest
- [x] Task 6: Package documentation in `schema/docs` (AC: 4, 5)
  - [x] Per-Block-type renderer spec (every field, its semantics, required/optional, budgets pointer); the Slide spec enumerates the exact allowed Markdown constructs and the strip-don't-error rule for disallowed ones
  - [x] Record the citations reading explicitly: lesson-level "Citations" (FR-1) = aggregation of per-Block embedded citations, no duplicate lesson-level storage (AD-5: embedded copy authoritative) — this is how AC 1's "Citations in lesson metadata" is satisfied
  - [x] Record the inline-SVG rationale (stakeholder-ratified 2026-07-18): Diagram SVG is stored inline in the script to guarantee byte-exact review-gate integrity — what the Teacher approved is frozen in the Published Version, with no swappable asset path for diagrams; the 200 kB per-diagram budget is the size bound
  - [x] Versioning policy: MAJOR.MINOR, minor additive-only, major cannot-play (scripts newer than player build only), version bump + migration/compatibility note required per change
  - [x] Reserved-extensions record — V2: `teacher_turn`, `classmate_turn` Block types, AI Teacher persona/avatar, scripted classmate moments; V3: reactive multi-agent behaviour, adaptive replanning/branching metadata, streaming delivery. Record only — do not design or build.
- [x] Task 7: Wire tests into the CI workflow; verify both wrappers agree on the full corpus (AC: 3)

## Dev Notes

> **All `[ASSUMPTION]` tags in this file were confirmed by john 2026-07-18** — they stand as accepted defaults; do not re-open them. Two items were explicitly ratified with overrides: inline Diagram SVG (see Block payloads + Task 6) and the `$id` base `https://schema.edon.education/` (see Architecture compliance).

### Why this story is first

The schema is the product's keystone (I-3): the single content contract between pipeline, Player, Authoring, and all future renderers. Every later epic consumes this package. The PRD sequencing directive is explicit: "schema package first" (addendum §2). Get the shapes right here; a wrong required field is a breaking change later.

### Scope fence

**In scope:** `/schema` package only — schema docs, fixtures, js + py validator wrappers, docs, minimal bootstrap + minimal CI.
**Out of scope (do not build):**
- Pydantic mirror models + CI equivalence proof (AD-2) — lands with the backend (Story 1.2+)
- `budgets.json` and its JSON Schema — Story 1.2 AC
- `normalise_key` shared fixture vector in `/schema` fixtures — Story 2.4 AC (leave directory room, create nothing)
- Simulation postMessage protocol v1 document in `/schema` — Epic 10 (Story 10.1); only the Block payload fields land now
- Any V2/V3 reserved extension (record in docs only)
- Player-side unknown-block *rendering* behavior — Story 4.9 exercises it; this story only ships the fixtures that make it testable

### The lesson envelope (design decisions, tagged)

```jsonc
{
  "schema": "1.0",                     // required; MAJOR.MINOR string — schema-validated by pattern ^\d+\.\d+$ ONLY (no const); wrappers parse the major before validation
  "lessonId": "…uuid…",                // required [ASSUMPTION: UUID string per spine ID convention]
  "tenantId": "…uuid…",                // required (FR-1: missing tenant fails validation)
  "courseRef": "…",                    // required opaque string — LMS-agnostic; Moodle mapping lives in the plugin (AD-16)
  "curriculumRef": {                   // required (AD-2; Teacher-correctable in review, source flips to "teacher")
    "value": "…", "source": "pipeline" // source ∈ "pipeline" | "teacher"
  },
  "version": 0,                        // required integer ≥ 0 [ASSUMPTION: Drafts carry 0; publish stamps n ≥ 1 — satisfies FR-1 "missing version metadata fails validation" while Drafts exist pre-publish]
  "title": "…",                        // required (Player top bar, Lesson card)
  "language": "en-NG",                 // required, loose BCP-47 pattern ^[a-zA-Z]{2,3}(-[a-zA-Z0-9]+)*$ — do NOT attempt full RFC 5646 validation in JSON Schema [ASSUMPTION: one lesson-level tag satisfies NFR-8 "text fields carry a language tag"; UX treats it as singular ("the Lesson Script's language tag" — voice preference, lang attributes). No per-field tags in v1.0; a per-block override is an additive minor later]
  "blocks": []                         // required, ordered; order is normative for playback (FR-13)
}
```

Citations note: FR-1 lists "Citations" in lesson metadata; AD-5 makes the **embedded per-Block copy authoritative** (projected server-side to a query table). Reading: citations live per-Block only; the Student-facing lesson-level "Sources" list is an aggregation, not duplicate storage `[ASSUMPTION — flagged for sign-off]`. Schema requires a `citations` array on every block (may be empty); "Draft carries ≥ 1 Citation" (FR-6) is a pipeline invariant enforced in Story 2.3, not expressible cleanly in JSON Schema.

### Base block envelope

Every block: `id` (required string — the stable slot id minted at plan stage, AD-23; all citations, view marks, patches, progress rows key on it), `type` (required string), `title` (required `[ASSUMPTION: required on every block — UX needs it for the Block rail, "Block n of N — {title}" announcements, completion tick list, generation progress rows; AD-2 doesn't pin it]`), `citations[]` (required array of citation objects, may be empty).

**Unknown-type tolerance is a validator design requirement:** blocks whose `type` is one of the six validate strictly against their per-type schema; blocks with any other `type` validate against the base envelope only and PASS (minor forward-compat — the unknown-block fixture is a *valid* fixture). Implement with `if/then` per known type + base-envelope fallback; do not use a closed `oneOf` over six types.

### Citation object (AD-2 pinned; verified against the real recorded fixtures)

Required: `sourceChunkId`, `documentTitle`, `excerpt`. Optional: `locator`, `documentId`, `tags`.
Mapping from the live edon-rag v1.2 response (see `fixtures/edon-rag/01_basic_query.json` — real production recordings): `chunk_id → sourceChunkId`, `document_id → documentId`, `document_title → documentTitle`, `text → excerpt`, `locator → locator` (page-based string e.g. `"Page 6"`, **nullable in the contract** — hence the mandatory no-locator fixture). Chunk ids are DB row ids — stable in normal operation but not guaranteed forever; **citation integrity inside immutable Published Versions rests on stored `excerpt` + `documentTitle`, never on id dereference** (contract §3 stability note). That is why only those fields are required.

### Block payloads (per type)

| Type | Fields |
|---|---|
| `slide` | `body` (required, Markdown-subset string `[ASSUMPTION: allowed constructs exactly — paragraphs, headings (##/###), bold, italic, ordered/unordered lists; images, raw HTML, and links forbidden (UX: "static rich text", never text-in-images). Renderers strip/ignore disallowed constructs, never error]`) |
| `narration` | `text` (required — always-available transcript, A-9; primary modality), `audioRef` (optional assetRef — publish-time TTS lands it in Story 3.8; schema carries the field now) |
| `quiz` | `questions[]` (required, min 1). Each: `id` (required), `type: "multipleChoice" \| "shortAnswer"`, `prompt` (required), `feedback` (required string, shown after answer `[ASSUMPTION: one feedback string per question, not per option]`). MC adds: `options[] {id, text}` (min 2), `correctOptionId` (required; must reference an option id — JSON Schema alone can't express this, so **both wrappers implement the referential check inside `validate()`** with identical semantics; the dangling-`correctOptionId` fixture proves parity). Short-answer adds: `acceptedAnswers[]` (required, min 1, Teacher-editable — OQ-4; normalised matching happens in Player/server code, not schema). Scoring: 1 point per question `[ASSUMPTION: no points field in v1.0; AD-15 fractions = correct/total. Adding weights later is an additive minor]` |
| `diagram` | `svg` (required string — sanitised SVG stored inline **[RATIFIED by stakeholder 2026-07-18]**: inline is the design intent — it guarantees byte-exact review-gate integrity (what the Teacher approved is frozen in the Published Version; no swappable asset path for diagrams); the AD-13 gate sanitises before any persist; ≤ 200 kB per-diagram budget is the size bound, checked by pipeline validators, not schema), `altText` (required), `longDescription` (optional), `caption` (optional) |
| `model3d` | `modelRef` (required assetRef), `poster` (required poster object), `annotations[]` (required, may be empty): `{number, text, anchor {x,y,z} optional [ASSUMPTION: viewer marker anchor shape]}` — annotation text is Teacher-editable (A-28). Licence/attribution stays in library asset metadata + frozen manifest (AD-9), NOT duplicated in the script; the viewer renders it from asset metadata (FR-16) |
| `simulation` | `mode` (required, `"template" \| "freecode"`), `templateId` (required iff template), `bundleRef` (required assetRef iff freecode), `name` (required — frame header strip), `params[]` (required descriptor array, AD-12 pinned shape: `{id, label, type, min, max, step, default}`), `paramsDescription` (required string — Floor-tier text alternative), `poster` (required poster object) |

Shared shapes:
- **assetRef** `{ref: string matching ^asset://, transferSize: integer bytes ≥ 0}` — `transferSize` required (AD-2: every heavy-asset reference carries it; populated at assemble/freeze; tap-to-load labels and the Constrained ceiling read only this field).
- **poster** `{image: assetRef, altText: required, longDescription: optional, caption: required one-line explanation}` — UX: poster must "stand alone pedagogically"; posters are required first-class data for Model3D/Simulation (FR-18 — also the flag-off and no-WebGL path), auto-load default per the device posture.
- `altText`/`longDescription` on Diagram Blocks and posters are the **stakeholder-approved text-alternative contract** (EXPERIENCE.md § Rulings item 15, approved in full 2026-07-17): pipeline populates at creation, Teachers edit as plain text in review.

### Version-mismatch semantics (document verbatim in /schema/docs)

- Same major, any minor (incl. future minor like `"1.7"`): validate; unknown block types and unknown fields are ignored/passed through. Minor bumps are additive only.
- Higher major than the consumer supports (e.g. `"2.0"`): **distinct `unsupportedMajor` outcome** from both wrappers — never a generic validation-error list (the Player maps this to the designed can't-play state: "This lesson needs a newer version of the player…"). Applies only to scripts *newer* than the consumer; players never drop support for a shipped major — published lessons stay playable forever (I-3).
- **Ordering is pinned:** the wrappers parse `schema` and run the major check FIRST, short-circuiting — a future-major script returns `{ok: false, unsupportedMajor: true, errors: []}` even if it also has schema errors (the future-major-and-invalid fixture proves this in both languages).
- Every schema change: version bump + migration/compatibility note in `/schema/docs`.

### Wrapper API contract (both languages, same shape)

`validate(scriptObject) → {ok: bool, unsupportedMajor: bool, errors: [{path, message}]}` `[ASSUMPTION: exact result shape — pick field names once, both wrappers mirror]`. Errors must be attributable to a specific block + field (UX pins validation errors inline to the offending field — the error `path` is what makes that possible). Both test suites iterate the same `expectations.json`; "agreement" = identical outcome classification per fixture, asserted mechanically.

### Architecture compliance checklist

- JSON Schema **2020-12** dialect explicitly (`$schema` on every document) — AD-2
- **camelCase** all script fields (platform API is snake_case — different convention, do not mix) — spine Conventions
- **No TypeScript** in `schema/js` — [HARD] §2, CI lint gate arrives in 1.2 but the rule binds now
- Permissive licences only (ajv MIT, jsonschema MIT) — NFR-7; clean-room: no code copied from any copyleft source, never fetch OpenMAIC
- No runtime validation in the Player — the js wrapper is toolchain/CI-only (AD-10); don't design the wrapper around browser bundling
- Schema files get stable `$id` URIs under **`https://schema.edon.education/lesson/1.0/…`** (stakeholder-ratified 2026-07-18: must be a stakeholder-controlled domain — these identifiers persist forever in published lessons; do not use any other base)

### Library versions (spine-verified 2026-07-17 — current as of yesterday, no re-research needed)

- ajv **8.20.x** — use the 2020-12 build (the default `ajv` export is draft-07). **ESM pinned** (`"type": "module"` in schema/js): `import Ajv2020 from "ajv/dist/2020.js"`. Plain JS.
- jsonschema (py) **4.26.x** — `Draft202012Validator`; build the full `errors[]` from `iter_errors` (each error's `json_path`/`absolute_path` gives the pinned field path). Do not use `best_match` for the list — it returns a single error.
- Vitest + ESLint + Prettier (js), pytest + ruff (py) — the one toolchain (AR-25); per-story tool choices are not open.
- Node ≥ 20 LTS; Python 3.12.

### Testing requirements (DoD)

- Unit tests for schema validation are **mandatory [HARD]-rule protectors** (project-context §7): both suites green over the full corpus, agreement asserted.
- Negative-space tests: every "Invalid" fixture fails for the *expected reason* (assert on error path, not just `ok: false`).
- This story ships a pure package: no runtime service ⇒ no logs/telemetry/`.env.example` items apply. State that plainly in the completion notes — do not fabricate telemetry work to satisfy the DoD checklist.

### Project Structure Notes

```text
schema/                    # new — repo root (this repo is the edon-lesson monorepo)
  lesson/                  # JSON Schema 2020-12 documents (envelope + $defs + per-block)
  fixtures/                # corpus + expectations.json  (room reserved: normalise_key vector → 2.4)
  js/                      # npm workspace pkg, ajv wrapper — plain JS ONLY
  py/                      # python pkg, jsonschema wrapper
  docs/                    # renderer specs, versioning policy, reserved-extensions record
package.json               # new — npm workspaces root [ASSUMPTION: minimal]
.github/workflows/schema.yml  # new — minimal CI [ASSUMPTION: GitHub Actions]
docs/ fixtures/ _bmad*/    # existing — do not touch
```

Naming `[ASSUMPTION]`: npm package `@edon/lesson-schema`; py package `edon_lesson_schema`.

### Previous story / git intelligence

First story of the project — no predecessor. Git history is planning artifacts only. Pre-existing and load-bearing for this story: `docs/integrations/edon-rag-retrieval.md` (v1.2 final — citation source-of-truth), `fixtures/edon-rag/*.json` (real production recordings — copy realistic excerpt/locator values from them into schema citation fixtures rather than inventing shapes), `docs/adr/ADR-001..014`.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story-1.1] — story + ACs (verbatim)
- [Source: _bmad-output/planning-artifacts/architecture/architecture-2027_edon_sim_pro-2026-07-17/ARCHITECTURE-SPINE.md#AD-2] — schema law: versioning, pinned payload facts, citation required set
- [Source: ARCHITECTURE-SPINE.md#AD-10, #AD-11, #AD-12, #AD-17, #AD-23] — unknown-type omission; transferSize/budgets; simulation dual-mode + params descriptor; poster derivation; stable slot ids
- [Source: ARCHITECTURE-SPINE.md#Consistency-Conventions, #Stack] — casing, ids, toolchain, pinned versions
- [Source: prd.md §4.1 FR-1..FR-3; §4.2 FR-5/FR-6; §4.3 FR-10/FR-11; §4.4 FR-13..FR-18; §5 NFR-7/NFR-8; §13 A-9/A-21/A-26/A-28/A-31; §12 OQ-4/OQ-5/OQ-10] — requirement text incl. testable consequences
- [Source: prd addendum §2 (schema-first sequencing), §5 (TTS/audioRef amendment, V2 reserved names)]
- [Source: EXPERIENCE.md § Rulings item 15 (text-alternative contract approved in full); § Component Patterns → Player shell, Quiz block, Narration control, Poster fallback card; § Capability Tiers; § State Patterns (unknown-block, can't-play)]
- [Source: DESIGN.md § Components → Block rail, Quiz block, Model3D viewer, Poster fallback card]
- [Source: docs/integrations/edon-rag-retrieval.md §3 (response fields, locator nullability, chunk-id stability note)]
- [Source: _bmad-output/project-context.md §2 (no TypeScript [HARD]), §5 (clean-room, licences), §6 (schema-first principle), §7 (testing DoD)]

## Dev Agent Record

### Agent Model Used

claude-fable-5 (Claude Fable 5)

### Debug Log References

- `uv venv` defaulted to Python 3.11 (uv-managed default), violating the `requires-python = ">=3.12"` pin — recreated with `uv venv --python 3.12`. CI is unaffected (setup-python pins 3.12) but local runs need the explicit flag.
- Both test suites passed on first run after that fix: js 23/23, py 23/23.

### Completion Notes List

- All 5 ACs implemented and verified. 19-fixture corpus classified identically by both wrappers via the shared `expectations.json` manifest (agreement is asserted mechanically, per fixture, in both suites: 23 tests each — 19 corpus + 4 targeted error-attribution/short-circuit tests).
- The two validator-design rules from review are enforced by construction and by fixture: `schema` field is pattern-only (future-minor `"1.7"` fixture validates) and block schemas never set `additionalProperties: false` (the future-minor fixture carries an unknown field on a known block type).
- The `correctOptionId` referential check is implemented inside `validate()` in BOTH wrappers with identical semantics and an exact-match parity test on the error object.
- Major-check short-circuit pinned and proven: `future-major-invalid.json` (major 2 + missing tenantId) returns `{ok: false, unsupportedMajor: true, errors: []}` in both languages.
- Fixture note: the future-minor fixture uses a neutral fabricated block type (`callout`), deliberately NOT the reserved V2 names (`teacher_turn` etc.) — using those would brush against the record-only fence.
- Citation fixtures use real values from the recorded production edon-rag fixtures (`fixtures/edon-rag/`), not invented shapes.
- DoD scope note (per story § Testing requirements): this story ships a pure package — no runtime service exists, so structured-logging/telemetry/`.env.example` DoD items do not apply. Mandatory [HARD]-protector unit tests (schema validation) are in place in both languages.
- Deferred to Story 1.2 as fenced: ESLint/Prettier/ruff configs (one-toolchain gate set), root uv lockfile, licence-audit + no-TypeScript CI gates. The minimal CI workflow notes this in comments.

### Change Log

- 2026-07-19: Implemented Story 1.1 — /schema package: JSON Schema 2020-12 documents (envelope + shared defs + six block types), 19-fixture corpus + expectations manifest, ajv (js/ESM) and jsonschema (py) validator wrappers with identical `validate()` semantics, renderer/versioning/reserved-extensions docs, minimal monorepo bootstrap (npm workspaces root, py package, GitHub Actions workflow).
- 2026-07-19: External review passed; all seven fix-pass assumptions confirmed by stakeholder (incl. UNLICENSED). Story marked done and merged. Carry-forward recorded on Story 3.7: "Published Version contains ≥ 1 block" is a publish-time invariant (not a schema rule — drafts start empty by design).
- 2026-07-19: Review fix pass (stakeholder-approved batches A/B/D/E + C rulings): regex engine parity (ASCII `[0-9]`, `re.fullmatch`, `(?!\n)$` schema-pattern guards — probes `"2.0\n"`, `"1.0\n"`, Arabic-Indic digits now reject identically in both languages); ajv if/then error-cascade filtered (error payloads now path-identical across languages, one error per invalid fixture); py schemas ship as package data with byte-equality drift test (non-editable install proven); js package marked private/UNLICENSED; uniqueness enforcement in both wrappers' referential layer (block ids / question ids per quiz / option ids per question) with fixtures; question-type closed-set rule recorded in versioning.md; `assetRef.ref` tightened to `^asset://.+`; expectations manifest carries per-fixture expected error path+message asserted in both suites; fixture-directory parity test; CI `permissions: contents: read` + dependency caching; `.gitignore` build/. Corpus now 27 fixtures; js 35 tests, py 36 tests, all green.

### File List

- package.json (new — npm workspaces root)
- package-lock.json (new — generated by npm install)
- .gitignore (new)
- .github/workflows/schema.yml (new — minimal CI: js + py suites)
- schema/lesson/1.0/lesson.schema.json (new — envelope)
- schema/lesson/1.0/defs.schema.json (new — assetRef, citation, poster, blockBase)
- schema/lesson/1.0/blocks/slide.schema.json (new)
- schema/lesson/1.0/blocks/narration.schema.json (new)
- schema/lesson/1.0/blocks/quiz.schema.json (new)
- schema/lesson/1.0/blocks/diagram.schema.json (new)
- schema/lesson/1.0/blocks/model3d.schema.json (new)
- schema/lesson/1.0/blocks/simulation.schema.json (new)
- schema/fixtures/expectations.json (new — cross-language agreement manifest)
- schema/fixtures/valid/full-six-block-lesson.json (new)
- schema/fixtures/valid/minimal-slide-quiz.json (new)
- schema/fixtures/valid/narration-no-audioref.json (new)
- schema/fixtures/valid/no-locator-citation.json (new)
- schema/fixtures/forward-compat/unknown-block-type.json (new)
- schema/fixtures/forward-compat/future-minor.json (new)
- schema/fixtures/forward-compat/future-major.json (new)
- schema/fixtures/forward-compat/future-major-invalid.json (new)
- schema/fixtures/invalid/missing-schema.json (new)
- schema/fixtures/invalid/missing-tenant.json (new)
- schema/fixtures/invalid/missing-version.json (new)
- schema/fixtures/invalid/block-missing-id.json (new)
- schema/fixtures/invalid/block-missing-citations.json (new)
- schema/fixtures/invalid/block-missing-title.json (new)
- schema/fixtures/invalid/citation-missing-excerpt.json (new)
- schema/fixtures/invalid/simulation-missing-mode.json (new)
- schema/fixtures/invalid/quiz-mc-missing-correct-option.json (new)
- schema/fixtures/invalid/quiz-mc-dangling-correct-option.json (new)
- schema/fixtures/invalid/quiz-short-answer-empty-accepted.json (new)
- schema/fixtures/invalid/duplicate-block-id.json (new — review fix pass, C1)
- schema/fixtures/invalid/quiz-duplicate-question-id.json (new — review fix pass, C1)
- schema/fixtures/invalid/quiz-duplicate-option-id.json (new — review fix pass, C1)
- schema/fixtures/invalid/assetref-missing-transfersize.json (new — review fix pass, D2)
- schema/fixtures/invalid/assetref-bad-scheme.json (new — review fix pass, D2)
- schema/fixtures/invalid/assetref-empty-ref.json (new — review fix pass, C3/D2)
- schema/fixtures/invalid/poster-missing-alttext.json (new — review fix pass, D2)
- schema/fixtures/invalid/poster-missing-caption.json (new — review fix pass, D2)
- schema/py/src/edon_lesson_schema/schemas/lesson/1.0/ (new — review fix pass, B1: packaged schema copies, drift-tested against schema/lesson/1.0)
- schema/js/package.json (new — @edon/lesson-schema, ESM, plain JS)
- schema/js/src/index.js (new — ajv 8.20 Ajv2020 wrapper)
- schema/js/test/validate.test.js (new — Vitest, 23 tests)
- schema/py/pyproject.toml (new — edon-lesson-schema)
- schema/py/src/edon_lesson_schema/__init__.py (new)
- schema/py/src/edon_lesson_schema/validator.py (new — jsonschema 4.26 Draft202012Validator wrapper)
- schema/py/tests/test_validate.py (new — pytest, 23 tests)
- schema/docs/README.md (new — package overview, validator contract, decisions of record)
- schema/docs/block-types.md (new — renderer spec per block type)
- schema/docs/versioning.md (new — MAJOR.MINOR policy + compatibility-notes table)
- schema/docs/reserved-extensions.md (new — V2/V3 record-only list)
- _bmad-output/implementation-artifacts/1-1-lesson-script-schema-v1-0-package.md (modified — this file)
- _bmad-output/implementation-artifacts/sprint-status.yaml (modified — status transitions)
